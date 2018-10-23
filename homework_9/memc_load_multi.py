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
SENTINEL = '<END>'
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


def pack_appsinstalled(appsinstalled, device_memc, dry_run=False):
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

    if dry_run:
        logging.debug("%s - %s -> %s" % (memc_addr, key, str(ua).replace("\n", " ")))
    else:
        return errors, memc_addr, key, packed


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


class MemcWorker(threading.Thread):

    def __init__(self, memc_client, memc_queue, result_queue):
        threading.Thread.__init__(self)
        self.memc_queue = memc_queue
        self.result_queue = result_queue
        self.memc_client = memc_client
        self.errors = 0
        self.processed = 0

    def send_results(self):
        self.result_queue.put({'errors': self.errors, 'processed': self.processed})
        self.errors = 0
        self.processed = 0

    def run(self):
        while True:
            val = self.memc_queue.get()
            if val == SENTINEL:
                self.memc_queue.put(SENTINEL)                   # Put SENTINEL back for another Memc worker
                break
            dev_type, memc_addr, key, packed = val
            ok = self.memc_client.write(dev_type, memc_addr, key, packed)
            if ok:
                self.processed += 1
            else:
                self.errors += 1
            if self.errors > 1000 or self.processed > 1000:     # Saving preliminary results
                self.send_results()
        logging.info("MemcWorker {} finished task".format(self.name))
        self.send_results()


def prepare_protobuf(appsinstalled, memc_queue, device_memc):
    '''Prepares protobuf pack for Memcache load'''
    errors, memc_addr, key, packed = pack_appsinstalled(appsinstalled, device_memc)
    memc_queue.put((appsinstalled.dev_type, memc_addr, key, packed))


def parse_file(fn, memc_queue, result_queue, device_memc):
    errors = 0
    try:
        with gzip.open(fn, 'rb') as fd:
            for line_num, line in enumerate(fd):
                line = line.strip()
                if not line:
                    continue
                appsinstalled = parse_appsinstalled(line)
                if not appsinstalled:
                    errors += 1
                    continue
                prepare_protobuf(appsinstalled, memc_queue, device_memc)
        result_queue.put({'errors': errors, 'processed': 0})
    except:
        logging.exception("Error reading file: %s" % (fn))
    logging.info("LineWorker finished task: file {}, errors={}".format(fn, errors))

def dot_rename(path):
    head, fn = os.path.split(path)
    # atomic in most cases
    os.rename(path, os.path.join(head, "." + fn))


def start_line_processes(pattern, memc_queue, result_queue, device_memc):
    '''Parses files to strings and send them to work_queue'''
    line_processes = []
    for fn in glob.iglob(pattern):
        logging.info('Processing %s' % fn)
        line_processes.append(mp.Process(target=parse_file, args=(fn, memc_queue, result_queue, device_memc)))

    for p in line_processes:
        p.start()


def start_memc_workers(memc_queue, result_queue):
    '''Read packages from memc_queue and send them to Memcache servers'''
    memc_client = MemcClient()
    for w in range(0, opts.workers):
        logging.info("Starting memc worker %s" % w)
        memc_worker = MemcWorker(memc_client, memc_queue, result_queue)
        memc_worker.start()


def main(options):
    device_memc = {
        "idfa": options.idfa,
        "gaid": options.gaid,
        "adid": options.adid,
        "dvid": options.dvid,
    }

    memc_queue = mp.Queue(maxsize=300000)
    result_queue = Queue()
    processed = 0
    errors = 0

    start_line_processes(options.pattern, memc_queue, result_queue, device_memc)
    start_memc_workers(memc_queue, result_queue)

    # Waiting until all workers finish their tasks
    while not memc_queue.empty():
        logging.info("Memc queue: {}, result queue: {}".format(memc_queue.qsize(), result_queue.unfinished_tasks))
        time.sleep(10)

    # Closing MemcWorkers
    memc_queue.put(SENTINEL)

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
    op.add_option("--idfa", action="store", default="35.238.204.0:11211")
    op.add_option("--gaid", action="store", default="107.178.221.100:11211")
    op.add_option("--adid", action="store", default="35.238.204.0:11211")
    op.add_option("--dvid", action="store", default="107.178.221.100:11211")
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
