#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import gzip
import sys
import glob
import logging
import collections
import time
from optparse import OptionParser
import appsinstalled_pb2
import memcache
import threading
import multiprocessing as mp
from queue import Queue

CONNECTION_RETRY_TIMEOUT = 20
CONNECTION_TIMEOUT = 5
NORMAL_ERR_RATE = 0.01
AppsInstalled = collections.namedtuple("AppsInstalled", ["dev_type", "dev_id", "lat", "lon", "apps"])


def parse_appsinstalled(line):
    line_parts = line.decode("utf-8").strip().split("\t")
    if len(line_parts) < 5:
        return
    dev_type, dev_id, lat, lon, raw_apps = line_parts
    if not dev_type or not dev_id:
        return
    try:
        apps = [int(a.strip()) for a in raw_apps.split(",")]
    except ValueError:
        apps = [int(a.strip()) for a in raw_apps.split(",") if a.isidigit()]
        logging.info("Not all user apps are digits: `%s`" % line)
    try:
        lat, lon = float(lat), float(lon)
    except ValueError:
        logging.info("Invalid geo coords: `%s`" % line)
    return AppsInstalled(dev_type, dev_id, lat, lon, apps)


def insert_appsinstalled(appsinstalled, device_memc, dry_run=False, line_num=0):
    errors = 0
    memc_addr = device_memc.get(appsinstalled.dev_type)
    if not memc_addr:
        errors += 1
        logging.error("Unknown device type: %s" % appsinstalled.dev_type)
        return errors

    ua = appsinstalled_pb2.UserApps()
    ua.lat = appsinstalled.lat
    ua.lon = appsinstalled.lon
    key = "%s:%s" % (appsinstalled.dev_type, appsinstalled.dev_id)
    ua.apps.extend(appsinstalled.apps)
    packed = ua.SerializeToString()

    # @TODO persistent connection
    # @TODO retry and timeouts!

    if dry_run:
        logging.debug("%s - %s -> %s" % (memc_addr, key, str(ua).replace("\n", " ")))
    else:
        #result = memc_client.write(appsinstalled.dev_type, memc_addr, key, packed)
        return errors, appsinstalled.dev_type, memc_addr, key, packed


def prototest():
    sample = "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23\ngaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
    for line in sample.splitlines():
        dev_type, dev_id, lat, lon, raw_apps = line.strip().split("\t")
        apps = [int(a) for a in raw_apps.split(",") if a.isdigit()]
        lat, lon = float(lat), float(lon)
        ua = appsinstalled_pb2.UserApps()
        ua.lat = lat
        ua.lon = lon
        ua.apps.extend(apps)
        packed = ua.SerializeToString()
        unpacked = appsinstalled_pb2.UserApps()
        unpacked.ParseFromString(packed)
        assert ua == unpacked


class MemcClient():

    def __init__(self):
        self.memc_pool = {}

    def write(self, dev_type, memc_addr, key, packed):
        if self.memc_pool.get(dev_type) == None:
            self.memc_pool[dev_type] = memcache.Client([memc_addr], dead_retry=CONNECTION_RETRY_TIMEOUT, socket_timeout=CONNECTION_TIMEOUT)
            logging.info("Opening Memcache connection, dev_type={} addr={}".format(dev_type, memc_addr))

        if self.memc_pool[dev_type].servers[0]._get_socket():  # connection established
            result = self.memc_pool[dev_type].set(key, packed)
            if not result:
                logging.exception("Cannot write to memc %s: %s" % (memc_addr, e))
                return False
        else:
            logging.exception("Error connecting to %s" % (memc_addr))
            return False
        return True


def prepare_protobuf(work_queue, memc_queue, result_queue, device_memc):
    '''Prepares protobuf pack for Memcache load'''
    tries = 0
    while True:
        line_num, appsinstalled = work_queue.get()
        errors, dev_type, memc_addr, key, packed = insert_appsinstalled(appsinstalled, device_memc, line_num=line_num)
        memc_queue.put((dev_type, memc_addr, key, packed))
        result_queue.put({'errors': errors, 'processed': 0})
        if tries == 2:
            break
        if work_queue.empty():
            logging.info("Protobuf process: work queue is empty, waiting ...")
            tries += 1
            time.sleep(3)
        else:
            tries = 0
    logging.info('Protobuf process: work finished')


class MemcWorker(threading.Thread):

    def __init__(self, memc_client, memc_queue, result_queue):
        threading.Thread.__init__(self)
        self.memc_queue = memc_queue
        self.result_queue = result_queue
        self.memc_client = memc_client
        self.task_complete = False
        self.running = True
        self.errors = 0
        self.processed = 0

    def disable(self):
        self.running = False

    def send_results(self):
        self.result_queue.put({'errors': self.errors, 'processed': self.processed})
        self.errors = 0
        self.processed = 0

    def run(self):
        """
        Thread run method. Reads packages from queue and sends them to Memcache server
        """
        while self.running:
            dev_type, memc_addr, key, packed = self.memc_queue.get()
            ok = self.memc_client.write(dev_type, memc_addr, key, packed)
            if ok:
                self.processed += 1
            else:
                self.errors += 1
            #print('Memc added: {} {}, queue: {} {}'.format(key, ok, self.memc_queue.qsize(), self.result_queue.unfinished_tasks))
            if self.errors > 1000 or self.processed > 1000:
                self.send_results()
        logging.info("MemcWorker {} finished task".format(self.name))
        self.send_results()


class LineWorker(threading.Thread):

    def __init__(self, work_queue, result_queue,  fn):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.fn = fn
        self.task_complete = False
        self.errors = 0

    def run(self):
        """
        Thread run method. Reads file line by line and sends them to queue
        """
        if self.fn is not None:
            try:
                with gzip.open(self.fn, 'rb') as fd:
                    self.task_complete = False
                    for line_num, line in enumerate(fd):
                        line = line.strip()
                        if not line:
                            continue
                        appsinstalled = parse_appsinstalled(line)
                        if not appsinstalled:
                            self.errors += 1
                            continue
                        self.work_queue.put((line_num, appsinstalled))
                self.task_complete = True
                self.result_queue.put({'errors': self.errors, 'processed': 0})
            except:
                logging.exception("Error reading file: %s" % (self.fn))
            logging.info("LineWorker finished task: file {}, errors={}".format(self.fn, self.errors))


def dot_rename(path):
    head, fn = os.path.split(path)
    # atomic in most cases
    os.rename(path, os.path.join(head, "." + fn))


def main(options):
    device_memc = {
        "idfa": options.idfa,
        "gaid": options.gaid,
        "adid": options.adid,
        "dvid": options.dvid,
    }

    # Init queues
    work_queue = mp.Queue(maxsize=100000)
    memc_queue = mp.Queue(maxsize=100000)
    result_queue = Queue()

    processed = 0
    errors = 0

    # Line workers: parse files to strings and send them to work_queue
    for fn in glob.iglob(options.pattern):
        logging.info('Processing %s' % fn)
        producer = LineWorker(work_queue, result_queue, fn)
        producer.start()

    # Protobuf process: prepares packages from work_queue strings and sends them to memc_queue
    proto_process = mp.Process(target=prepare_protobuf, args=(work_queue, memc_queue, result_queue, device_memc))
    proto_process.start()

    # Memc workers: read packages from memc_queue and send them to Memcache servers
    memc_client = MemcClient()
    memc_workers = []
    for w in range(0, opts.workers):
        logging.info("Starting memc worker %s" % w)
        memc_worker = MemcWorker(memc_client, memc_queue, result_queue)
        memc_worker.start()
        memc_workers.append(memc_worker)

    # Waiting until all workers finish their tasks
    while not work_queue.empty() or not memc_queue.empty():
        logging.info("Work queue: {}, memc queue: {}, result queue: {}".format(work_queue.qsize(), memc_queue.qsize(), result_queue.unfinished_tasks))
        time.sleep(10)

    # Closing MemcWorkers. Protobuf process and LineWorkers are closed by themselves
    for memc_worker in memc_workers:
        memc_worker.disable()
        logging.info("MemcWorker {} stopped".format(memc_worker))

    # Calculating stats
    while not result_queue.empty():
        result_worker = result_queue.get()
        processed += result_worker['processed']
        errors += result_worker['errors']
    logging.info("Total processed={} errors={}".format(processed, errors))
    err_rate = float(errors) / processed
    if err_rate < NORMAL_ERR_RATE:
        logging.info("Acceptable error rate ({:.5f}). Successfull load".format(err_rate))
    else:
        logging.error("High error rate ({:.5f} > {:.5f}). Failed load".format(err_rate, NORMAL_ERR_RATE))

    for fn in glob.iglob(options.pattern):
        dot_rename(fn)

    return True


if __name__ == '__main__':
    op = OptionParser()
    op.add_option("--workers", action="store", default=1)
    op.add_option("-t", "--test", action="store_true", default=False)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("--dry", action="store_true", default=False)
    op.add_option("--pattern", action="store", default="/data/appsinstalled/*.tsv.gz")
    op.add_option("--idfa", action="store", default="35.226.182.234:11211")
    op.add_option("--gaid", action="store", default="35.232.4.163:11211")
    op.add_option("--adid", action="store", default="35.226.182.234:11211")
    op.add_option("--dvid", action="store", default="35.232.4.163:11211")
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO if not opts.dry else logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    if opts.test:
        prototest()
        sys.exit(0)

    logging.info("Starting Memc loader with options: %s" % opts)
    start_time = time.time()
    try:
        opts.workers = int(opts.workers)
        main(opts)
    except Exception as e:
        logging.exception("Unexpected error: %s" % e)
        sys.exit(1)
    finally:
        elapsed_time = time.time() - start_time
        logging.info("Time elapsed: %s sec" % elapsed_time)
        print ("Work finished")
        sys.exit(0)

