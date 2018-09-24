#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import asyncio
import logging
import datetime

import time
from hashlib import sha1
from optparse import OptionParser

import aiohttp

START_URL = 'http://news.ycombinator.com'
EXCLUDE_URLS = ['news.ycombinator.com', 'www.ycombinator.com', 'github.com/HackerNews/API']
WAIT_PERIOD = 60


class Crawler():

    def __init__(self, opts):
        self.start_url = START_URL
        self.concurrency_level = 10
        self.cookie_jar = None
        self.current_url_id = 0
        self.save_dir = opts.save_dir
        self.failed_urls = []
        self.parsed_urls = {} # this should be stored in a key-value storage
        self.semaphore = asyncio.Semaphore(self.concurrency_level)
        logging.info("Starting crawler ... ")

    async def check_start_page(self, loop):
        async with aiohttp.ClientSession(loop=loop) as session:
            while True:
                logging.info("Checking start page ... ")
                await self.parse_start_page(loop, session)
                await asyncio.sleep(WAIT_PERIOD)
                logging.info("Total parsed urls: {}, total failed urls: {} ".format(len(self.parsed_urls),
                                                                                    len(self.failed_urls)))

    async def parse_start_page(self, loop, session):
        async with session.get(START_URL) as resp:
            try:
                content = await resp.text()
                url_pairs = self.parse_urls(content, self.start_url)
                parsed_before = 0

                for url_pair in url_pairs:
                    if not self.get_hash(url_pair[1]) in self.parsed_urls.values():
                        asyncio.ensure_future(self.execute_url(url_pair, session))
                    else:
                        parsed_before += 1
                logging.info("Found urls: {}, parsed before and skipped: {}".format(len(url_pairs), parsed_before))

            except asyncio.TimeoutError:
                pass

    def parse_urls(self, html, base_url):
        if html is None:
            logging.error("HTML is none")
            return

        checked_urls = []
        blocks = re.findall(r'\<tr class\=\'athing\' id=\'(.*?)\'\>(.*?)\<\/tr\>', html, re.S)
        for block in blocks:
            urls = re.findall(r'href=\"(http|https)://(.*?)\"', block[1])
            id = int(block[0])

            for url in urls:
                url_str = url[0] + '://' + url[1]
                exclude = False
                for exc in EXCLUDE_URLS:
                    if exc in url_str:
                        exclude = True
                if not exclude:
                    checked_urls.append([id, url_str])

        return checked_urls

    async def execute_url(self, url_pair, session):
        item_id, url = url_pair
        html = await self.fetch(url, session)

        if not html == None:
            url_id = self.get_current_id()
            self.parsed_urls[url_id] = self.get_hash(url)
            logging.info("Url #{}: got content, length={}".format(url_id, len(html)))

            asyncio.ensure_future(self.save_content(url_id, html))
            asyncio.ensure_future(self.save_comments(url_id, item_id))

        elif not url in self.failed_urls:
            self.failed_urls.append(url_pair)

    def get_hash(self, str):
        return sha1(str.encode("utf-8")).hexdigest()

    async def fetch(self, url, session):
        with (await self.semaphore):
            try:
                async with session.get(url) as response:
                    if response.status in [200, 201]:
                        data = await response.text()
                        return data
                    logging.error('Error reading url: {},  status: {}'.format(url, response.status))
                    return None
            except:
                #logging.info('Fetch return None')
                return None

    async def save_content(self, url_id, html):
        path = os.path.abspath(os.path.join(self.save_dir, "newsline_" + str(url_id)))
        try:
            if not os.path.isdir(path):
                os.mkdir(path)
            filename = os.path.join(path, 'page.html')
            with open(filename, 'w') as f:
                f.write(html)
                logging.info("Url #{}: content saved".format(url_id))
        except Exception as err:
            logging.exception("Can't save content to {}: {}".format(path, err))

    async def save_comments(self, url_id, item_id):

        logging.info("Saving comments {} {}".format(url_id, item_id))

        path = os.path.abspath(os.path.join(self.save_dir, "newsline_" + str(url_id)))
        try:
            if not os.path.isdir(path):
                os.mkdir(path)
            #filename = os.path.join(path, 'page.html')
            #with open(filename, 'w') as f:
            #    f.write(html)
            #    logging.info("Url #{}: content saved".format(url_id))
        except Exception as err:
            logging.exception("Can't save content to {}: {}".format(path, err))

    def get_current_id(self):
        self.current_url_id += 1
        return self.current_url_id





def main(opts):
    crawler = Crawler(opts)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawler.check_start_page(loop))
    loop.close()


if __name__ == '__main__':

    # Обработка параметров скрипта
    op = OptionParser()
    op.add_option("--dry", action="store_true", default=False)
    op.add_option("--log", action="store", default=None)
    op.add_option("--save_dir", action="store", default='./content/')
    op.add_option("--workers", action="store", default=1)
    (opts, args) = op.parse_args()

    # Инициализация лога и запуск скрипта
    logging.basicConfig(filename=opts.log, level=logging.INFO if not opts.dry else logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')

    main(opts)