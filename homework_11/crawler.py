#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import asyncio
import logging
import random
import aiohttp

from hashlib import sha1
from optparse import OptionParser

START_URL = 'https://news.ycombinator.com'
EXCLUDE_URLS = ['news.ycombinator.com', 'www.ycombinator.com', 'github.com/HackerNews/API']
WAIT_PERIOD = 60


class Crawler():

    def __init__(self, opts, loop):
        self.loop = loop
        self.start_url = START_URL
        self.concurrency_level = 20
        self.cookie_jar = None
        self.current_url_id = 0
        self.failed_urls = []
        self.parsed_urls = {} # this should be stored in a key-value storage
        self.semaphore = asyncio.Semaphore(self.concurrency_level)
        self.parser = Parser()
        self.saver = Saver(opts.save_dir)
        logging.info("Starting crawler ... ")

    async def check_start_page(self):
        '''Checking start page in infinite loop'''
        async with aiohttp.ClientSession(loop=self.loop) as session:
            while True:
                logging.info("Checking start page ... ")
                future = asyncio.Future()
                asyncio.ensure_future(self.parse_start_page(session, future))
                future.add_done_callback(self.execute_start_page_urls)

                await asyncio.sleep(WAIT_PERIOD)
                logging.info("Total parsed urls: {}, total failed urls: {} ".format(len(self.parsed_urls),
                                                                                    len(self.failed_urls)))

    async def parse_start_page(self, session, future):
        '''Parsing start page, searching URLs'''
        async with session.get(START_URL) as resp:
            try:
                content = await resp.text()
                url_pairs = self.parser.parse_urls(content)
                future.set_result((url_pairs, session))
            except asyncio.TimeoutError:
                pass

    def execute_start_page_urls(self, future):
        '''Starting parse process with found URLs'''
        url_pairs = future.result()[0]
        session = future.result()[1]
        parsed_before = 0
        for url_pair in url_pairs:
            if not self.get_hash(url_pair[1]) in self.parsed_urls.values():
                asyncio.ensure_future(self.execute_url(url_pair, session))
            else:
                parsed_before += 1
        logging.info("Found urls: {}, parsed before and skipped: {}".format(len(url_pairs), parsed_before))

    async def execute_url(self, url_pair, session):
        '''Process URL from start page news list'''
        item_id, url = url_pair
        html = await self.parser.fetch_url(self.semaphore, url, session)

        if not html == None:
            url_id = self.get_current_id()
            self.parsed_urls[url_id] = self.get_hash(url)
            logging.info("Url #{}: got main page, length={}".format(url_id, len(html)))
            asyncio.ensure_future(self.saver.save_page(self.loop, url_id, html))
            asyncio.ensure_future(self.get_comments(url_id, item_id, session))
        elif not url_pair in self.failed_urls:
            self.failed_urls.append(url_pair)

    def get_hash(self, str):
        '''URL hash'''
        return sha1(str.encode("utf-8")).hexdigest()

    async def get_comments(self, url_id, item_id, session):
        '''Get all comments on particular newsline'''

        comments_url = self.start_url + "/item?id=" + str(item_id)
        html = await self.parser.fetch_url(self.semaphore, comments_url, session, retry=5)
        if not html[0] == None:
            logging.info("Url #{}: got comment page, length={}".format(url_id, len(html)))
            asyncio.ensure_future(self.saver.save_comment_page(self.loop, url_id, html))
            com_urls = self.parser.parse_comments(html)
            logging.info("Url #{}: found {} links in comments".format(url_id, len(com_urls)))

            com_htmls = await self.parser.fetch_urls(self.semaphore, com_urls, session, retry=5)
            asyncio.ensure_future(self.saver.save_comment_url(self.loop, url_id, com_htmls))

    def get_current_id(self):
        self.current_url_id += 1
        return self.current_url_id


class Parser():

    async def fetch_url(self, semaphore, url, session, retry=1):
        '''Get URL content'''
        with (await semaphore):
            try:
                html = await self.get_response(url, session, retry=retry)
                return html
            except Exception as err:
                logging.error('Error reading url: {}: {}'.format(url, err))

    async def fetch_urls(self, semaphore, urls, session, retry=1):
        '''Get URLs content'''
        htmls = {}
        for url in urls:
            htmls[url] = self.fetch_url(semaphore, url, session, retry=retry)
        return htmls

    async def get_response(self, url, session, retry):
        '''Read page'''
        iter = 0
        while True:
            async with session.get(url) as response:
                if response.status in [200, 201]:
                    data = await response.text()
                    return data
                elif response.status in [301, 302, 307, 308]:
                    logging.info("Redirecting {} to {}".format(url, response.headers['Location']))
                    url = response.headers['Location']
                    iter += 1
                else:  # If any other status - try again
                    iter += 1
            if iter >= retry:
                logging.error('Error reading url: {},  status: {}, tries {}'.format(url, response.status, retry))
                return
            await asyncio.sleep(30 * random.random())

    def parse_urls(self, html):
        '''Search URLs on the page'''
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
        '''Search comments on page'''
        if html is None:
            logging.error("HTML is none")
            return

        checked_urls = []
        urls = re.findall(r'\<a href=\"(http|https):(.*?)\"', html)
        for url in urls:
            url_str = url[0] + ':' + url[1]
            url_str = url_str.replace('&#x2F;', '/')
            if not self.in_excluded(url_str):
                checked_urls.append(url_str)
        return checked_urls

    def in_excluded(self, url):
        '''Check if URL is in excluded list'''
        for exc in EXCLUDE_URLS:
            if exc in url:
                return True
        return False


class Saver():

    def __init__(self, save_dir):
        self.save_dir = save_dir

    async def save_page(self, loop, url_id, html):
        '''Save main news page'''
        await loop.run_in_executor(
            None, self.save_content, url_id, 'page.html', html)

    async def save_comment_page(self, loop, url_id, html):
        '''Save comment page'''
        await loop.run_in_executor(
            None, self.save_content, url_id, 'comments.html', html)

    async def save_comment_url(self, loop, url_id, htmls):
        '''Save comment URLs content'''
        num = 0
        for html in htmls:
            await loop.run_in_executor(
                None, self.save_content, url_id, 'comment_link_' + str(num) + '.html', html)
            num += 1

    def save_content(self, url_id, file, html):
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


def main(opts):
    loop = asyncio.get_event_loop()
    crawler = Crawler(opts, loop)
    loop.run_until_complete(crawler.check_start_page())
    loop.close()


if __name__ == '__main__':

    op = OptionParser()
    op.add_option("--log", action="store", default=None)
    op.add_option("--save_dir", action="store", default='./content/')
    (opts, args) = op.parse_args()

    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')

    main(opts)