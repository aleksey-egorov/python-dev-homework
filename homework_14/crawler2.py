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
WAIT_PERIOD = 30


class Crawler():

    def __init__(self):
        self.start_url = START_URL
        #self.parsers = [Parser(self.start_url)]
        self.concurrency_level = 10
        self.cookie_jar = None
        self.urls_count = 0
        logging.info("Starting crawler ... ")


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

        return checked_urls


    async def parse_start_page(self, loop, session):
        async with session.get(START_URL) as resp:
            try:
                content = await resp.text()
                urls = self.parse_urls(content, self.start_url)
                logging.info("Found urls: {}".format(len(urls)))

                for url in urls:
                    coro = asyncio.ensure_future(self.execute_url(url, session))

            except asyncio.TimeoutError:
                pass


    async def execute_url(self, url, session):
        html = await self.fetch(url, session)
        if not html == None:
            logging.info("Got content '{}': {}".format(url, len(html)))



    async def fetch(self, url, session):
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


    async def check_start_page(self, loop, opts):
        async with aiohttp.ClientSession(loop=loop) as session:
            while True:
                logging.info("Checking start page ... ")
                await self.parse_start_page(loop,session)
                await asyncio.sleep(WAIT_PERIOD)


def main():
    crawler = Crawler()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawler.check_start_page(loop, opts))
    loop.close()


if __name__ == '__main__':

    # Обработка параметров скрипта
    op = OptionParser()
    op.add_option("--dry", action="store_true", default=False)
    op.add_option("--log", action="store", default=None)
    op.add_option("--workers", action="store", default=1)
    (opts, args) = op.parse_args()

    # Инициализация лога и запуск скрипта
    logging.basicConfig(filename=opts.log, level=logging.INFO if not opts.dry else logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')

    main()