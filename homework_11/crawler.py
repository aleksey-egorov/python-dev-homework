#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import asyncio
import logging
import random

import time
from hashlib import sha1
from optparse import OptionParser

import aiohttp

START_URL = 'https://news.ycombinator.com'
EXCLUDE_URLS = ['news.ycombinator.com', 'www.ycombinator.com', 'github.com/HackerNews/API']
WAIT_PERIOD = 600


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
        '''Checking start page in infinite loop'''
        async with aiohttp.ClientSession(loop=loop) as session:
            while True:
                logging.info("Checking start page ... ")
                await self.parse_start_page(loop, session)
                await asyncio.sleep(WAIT_PERIOD)
                logging.info("Total parsed urls: {}, total failed urls: {} ".format(len(self.parsed_urls),
                                                                                    len(self.failed_urls)))

    async def parse_start_page(self, loop, session):
        '''Parsing start page, searching URLs'''
        async with session.get(START_URL) as resp:
            try:
                content = await resp.text()
                url_pairs = self.parse_urls(content)
                parsed_before = 0

                for url_pair in url_pairs:
                    if not self.get_hash(url_pair[1]) in self.parsed_urls.values():
                        asyncio.ensure_future(self.execute_url(url_pair, session))
                    else:
                        parsed_before += 1
                logging.info("Found urls: {}, parsed before and skipped: {}".format(len(url_pairs), parsed_before))

            except asyncio.TimeoutError:
                pass


    async def execute_url(self, url_pair, session):
        '''Process URL from start page news list'''
        item_id, url = url_pair
        html = await self.fetch(url, session)

        if not html == None:
            url_id = self.get_current_id()
            self.parsed_urls[url_id] = self.get_hash(url)
            logging.info("Url #{}: got main page, length={}".format(url_id, len(html)))

            asyncio.ensure_future(self.save_page(url_id, html))
            asyncio.ensure_future(self.get_comments(url_id, item_id, session))

        elif not url_pair in self.failed_urls:
            self.failed_urls.append(url_pair)


    def get_hash(self, str):
        '''URL hash'''
        return sha1(str.encode("utf-8")).hexdigest()


    async def fetch(self, url, session, retry=1):
        '''Get URL content'''
        with (await self.semaphore):
            try:
                for t in range(retry):
                    async with session.get(url) as response:
                        if response.status in [200, 201]:
                            data = await response.text()
                            #logging.info("Got url content {}, length={}".format(url, len(data)))
                            return data
                    if retry > 1:
                        await asyncio.sleep(30 * random.random())
                logging.error('Error reading url: {},  status: {}, tries {}'.format(url, response.status, retry))
                return None
            except:
                return None


    async def get_comments(self, url_id, item_id, session):
        '''Get all comments on particular newsline'''

        sleep_time = 60 * random.random()
        await asyncio.sleep(sleep_time)
        comments_url = self.start_url + "/item?id=" + str(item_id)

        html = await self.fetch(comments_url, session, retry=5)
        if not html == None:
            logging.info("Url #{}: got comment page, length={}".format(url_id, len(html)))
            asyncio.ensure_future(self.save_comment_page(url_id, html))
            com_urls = self.parse_comments(html)
            num = 0
            for com_url in com_urls:
                com_html = await self.fetch(com_url, session, retry=5)
                if not com_html == None:
                    logging.info("Url #{}: got comment url content, length={}".format(url_id, len(html)))
                    asyncio.ensure_future(self.save_comment_url(url_id, com_html, num))
                num += 1


    async def save_page(self, url_id, html):
        '''Save main news page'''
        await self.save_content(url_id, 'page.html', html)


    async def save_comment_page(self, url_id, html):
        '''Save comment page'''
        await self.save_content(url_id, 'comments.html', html)


    async def save_comment_url(self, url_id, html, num):
        '''Save comment URL content'''
        await self.save_content(url_id, 'comment_link_' + str(num) + '.html', html)


    def parse_urls(self, html):
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
                if not self.in_excluded(url_str):
                    checked_urls.append([id, url_str])
        return checked_urls


    def parse_comments(self, html):
        if html is None:
            logging.error("HTML is none")
            return

        checked_urls = []
        urls = re.findall(r'\<a href=\"(http|https):(.*?)\"', html)
        for url in urls:
            url_str = url[0] + ':' + url[1]
            if not self.in_excluded(url_str):
                checked_urls.append(url_str)
        return checked_urls


    async def save_content(self, url_id, file, html):
        if not os.path.isdir(os.path.abspath(self.save_dir)):
            os.mkdir(os.path.abspath(self.save_dir))
        path = os.path.abspath(os.path.join(self.save_dir, "newsline_" + str(url_id)))
        try:
            if not os.path.isdir(path):
                os.mkdir(path)
            filename = os.path.join(path, file)
            with open(filename, 'w') as f:
                f.write(html)
                logging.info("Url #{}: content saved, file {}".format(url_id, file))
        except Exception as err:
            logging.exception("Can't save content to {}: {}".format(path, err))


    def get_current_id(self):
        self.current_url_id += 1
        return self.current_url_id


    def in_excluded(self, url):
        for exc in EXCLUDE_URLS:
            if exc in url:
                return True
        return False




def main(opts):
    crawler = Crawler(opts)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawler.check_start_page(loop))
    loop.close()


if __name__ == '__main__':

    op = OptionParser()
    op.add_option("--log", action="store", default=None)
    op.add_option("--save_dir", action="store", default='./content/')
    (opts, args) = op.parse_args()

    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')

    main(opts)