#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import asyncio
import logging
import datetime

import time
from optparse import OptionParser

import aiohttp

START_URL = 'http://news.ycombinator.com'
EXCLUDE_URLS = ['news.ycombinator.com', 'www.ycombinator.com', 'github.com/HackerNews/API']


class Crawler():

    def __init__(self):
        self.start_url = START_URL
        self.parsers = [Parser(self.start_url)]
        self.concurrency_level = 10
        self.cookie_jar = None
        self.urls_count = 0

    def is_active(self):
        is_active = False
        for parser in self.parsers:
            if parser.active_session or len(parser.parsing_urls) > 0:
                is_active = True
        return is_active

    def run(self):
        logging.info('Crawler started')
        start_time = datetime.datetime.now()

        self.loop = asyncio.get_event_loop()

        try:
            semaphore = asyncio.Semaphore(self.concurrency_level)
            self.check_start_url(semaphore)
            #loop.run_until_complete(cls.init_parse(semaphore))
            #loop.run_until_complete(tasks)
            self.loop.run_forever()
        except KeyboardInterrupt:
            for task in asyncio.Task.all_tasks():
                task.cancel()

        finally:
            for parser in self.parsers:
                if parser.item is not None:
                    logging.info('Item "{}": {}'.format(parser.item, parser.item.count))

            end_time = datetime.datetime.now()
            #logging.info('Requests count: {}'.format(cls.urls_count))
            #logging.info('Error count: {}'.format(len(cls.error_urls)))
            logging.info('Time usage: {}'.format(end_time - start_time))
            logging.info('Crawler stopped')
            self.loop.close()

    def check_start_url(self, semaphore):
        tasks = [parser.run_task(self, semaphore) for parser in self.parsers]
        # loop.run_until_complete(cls.init_parse(semaphore))
        tasks_coro = asyncio.wait(tasks)
        self.loop.run_until_complete(tasks_coro)
        self.check_start_url(semaphore)
        #future.add_done_callback(self.callback)
        await asyncio.sleep(10)

    async def callback(self):
        await asyncio.sleep(10)
        logging.info("Callback!")



class Parser():

    def __init__(self, url):
        self.url = url
        self.item = []
        self.parsing_urls = []
        self.active_session = False
        self.done_urls = 0

    async def run_task(self, crawler, semaphore):
        logging.info("Processing {}".format(self.url))

        async with aiohttp.ClientSession(cookie_jar=crawler.cookie_jar) as session:
            self.active_session = True
            async with session.get(self.url) as resp:
                try:
                    content = await resp.text()
                    urls = self.parse_urls(content, self.url)
                    logging.info("Found urls: {}".format(urls))

                    for url in urls[:1]:
                        #print ("url={}".format(url))
                        coro = asyncio.ensure_future(self.execute_url(url, crawler, session, semaphore))

                except asyncio.TimeoutError:
                    pass

        logging.info("End processing {}".format(self.url))


    def parse_urls(self, html, base_url):
        if html is None:
            logging.error("HTML is none")
            return
        urls = re.findall(r'href=\"(http|https)://(.*?)\"', html)

        checked_urls = []
        for url in urls:
            url_str = url[0] + '://' + url[1]
            exclude = False
            for exc in EXCLUDE_URLS:
                if exc in url_str:
                    exclude = True
            if not exclude:
                checked_urls.append(url_str)

        logging.info("Found urls: {}".format(len(checked_urls)))
        return checked_urls



    async def execute_url(self, url, crawler, session, semaphore):
        html = await self.fetch(url, crawler, session, semaphore)
       # logging.info("HTML len={}".format(len(html)))
        html = ''
        if html is None:
            logging.error("{}: HTML is none".format(url))
            #crawler.error_urls.appendsel(url)
           # self.pre_parse_urls.put_nowait(url)
            return None

        #if url in crawler.error_urls:
        #    crawler.error_urls.remove(url)
        crawler.urls_count += 1
        #self.parsing_urls.remove(url)
        #self.done_urls.append(url)

        if self.item is not None:
            item = self.parse_item(html)
            #await item.save()
            #self.item.count_add()
           # logging.info('Parsed({}/{}): {}'.format(len(self.done_urls), len(self.filter_urls), url))
        else:
            crawler.parse(html)
           # logging.info('Followed({}/{}): {}'.format(len(self.done_urls), len(self.filter_urls), url))


    async def fetch(self, url, crawler, session, semaphore):
        with (await semaphore):
            #if callable(crawler.headers):
            #    headers = crawler.headers()
            #else:
            #    headers = crawler.headers
            async with aiohttp.ClientSession(cookie_jar=crawler.cookie_jar) as session:
                async with session.get(url) as response:
                    try:
                        if response.status in [200, 201]:
                            data = await response.text()
                            return data
                        logging.error('Error: {} {}'.format(url, response.status))
                        return None
                    except:
                        logging.info('Fetch return None')
                        return None

    def parse_item(self, html):
        pass



def main(options):
    crawler = Crawler()
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
