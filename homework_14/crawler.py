#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import asyncio
import logging
import datetime
from optparse import OptionParser

import aiohttp


class Crawler():

    def __init__(self, start_url):
        self.start_url = start_url
        self.parsers = [Parser(start_url), Parser(start_url+'?123')]
        self.concurrency_level = 10

    def run(self):
        logging.info('Crawler started')
        start_time = datetime.datetime.now()

        loop = asyncio.get_event_loop()

        try:
            semaphore = asyncio.Semaphore(self.concurrency_level)
            tasks = [parser.run_task(self, semaphore) for parser in self.parsers]
            #loop.run_until_complete(cls.init_parse(semaphore))
            tasks_coro = asyncio.wait(tasks)
            loop.run_until_complete(tasks_coro)
        except KeyboardInterrupt:
            for task in asyncio.Task.all_tasks():
                task.cancel()
            loop.run_forever()
        finally:
            for parser in self.parsers:
                if parser.item is not None:
                    logging.info('Item "{}": {}'.format(parser.item, parser.item.count))

            end_time = datetime.datetime.now()
            #logging.info('Requests count: {}'.format(cls.urls_count))
            #logging.info('Error count: {}'.format(len(cls.error_urls)))
            logging.info('Time usage: {}'.format(end_time - start_time))
            logging.info('Spider stopped')
            loop.close()


class Parser():

    def __init__(self, url):
        self.url = url
        self.item = []

    async def run_task(self, crawler, semaphore):
        logging.info("Processing {}".format(self.url))

        async with aiohttp.ClientSession(cookie_jar=crawler.cookie_jar) as session:
            while crawler.is_active():
                try:
                    url = await asyncio.wait_for(self.pre_parse_urls.get(), 5)
                    self.parsing_urls.append(url)
                    asyncio.ensure_future(self.execute_url(url, crawler, session, semaphore))
                except asyncio.TimeoutError:
                    pass

        logging.info("End processing {}".format(self.url))

    def execute_url(self):
        pass

    def parsing_urls(self):
        pass



def main(options):

    url = 'http://news.ycombinator.com'
    crawler = Crawler(url)
    crawler.run()



if __name__ == "__main__":

    # Обработка параметров скрипта
    op = OptionParser()
    op.add_option("--dry", action="store_true", default=False)
    op.add_option("--log", action="store", default=None)
    op.add_option("--workers", action="store", default=1)
    (opts, args) = op.parse_args()

    # Инициализация лога и запуск скрипта
    logging.basicConfig(filename=opts.log, level=logging.INFO if not opts.dry else logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')

    try:
        main(opts)
    except:
        logging.exception("Exception raised")
