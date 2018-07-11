#!/usr/bin/env python
# -*- coding: utf-8 -*-


import log_analyzer as la
import unittest
import os

class LogAnalyzerTest(unittest.TestCase):

    def test_get_latest_file(self):
        """Тестирование поиска файла с последней датой """

        logdir = './log'
        file_pattern = 'nginx-test-ui.log'
        date = '20170623'
        date_form = '2017.06.23'
        file_name = file_pattern+'-' + date + '.gz'

        f = open(logdir+ '/'+ file_name, 'w')
        f.close()

        latest = la.get_latest_file(logdir, file_pattern)
        os.unlink(logdir+ '/'+ file_name)

        self.assertEqual(latest.filename, file_name)
        self.assertEqual(latest.date, date_form)


    def test_prepare_stats(self):
        """Тестирование подготовки сводных данных"""

        logdir = './log'
        file_pattern = 'nginx-test-ui.log'
        date = '20170623'
        file_name = file_pattern + '-' + date

        f = open(logdir + '/' + file_name, 'w')
        f.write("1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] \"GET /api/v2/banner/25019354 HTTP/1.1\" 200 927 \"-\" \"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5\" \"-\" \"1498697422-2190034393-4708-9752759\" \"dc7161be3\" 0.390\n")
        f.write("1.196.116.32 -  - [29/Jun/2017:03:52:22 +0300] \"GET /api/v2/banner/25019354 HTTP/1.1\" 200 927 \"-\" \"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5\" \"-\" \"1498697422-2190034393-4708-9752759\" \"123323be3\" 0.330\n")
        f.write("1.196.116.32 -  - [29/Jun/2017:03:54:22 +0300] \"GET /api/v2/banner/25022354 HTTP/1.1\" 200 927 \"-\" \"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5\" \"-\" \"1498697422-2190034393-4708-9752759\" \"dc7161be3\" 0.270\n")
        f.write("1.196.116.32 -  - [29/Jun/2017:03:55:22 +0300] \"GET /api/v2/banner/25019354 HTTP/1.1\" 200 927 \"-\" \"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5\" \"-\" \"1498697422-2190034393-4708-9752759\" \"123323be3\" 1.330\n")

        f.close()

        stats = la.prepare_stats(la.read_lines(logdir + '/' + file_name, 0.95))

        self.assertEqual(stats.data['/api/v2/banner/25022354'][0], 0.27)
        self.assertEqual(stats.data['/api/v2/banner/25019354'][1], 0.33)

        os.unlink(logdir + '/' + file_name)


    def test_process_line(self):
        """Тестирование парсинга строк"""

        request = "GET /api/v2/banner/25023278 HTTP/1.1"
        request_time = "0.841"
        log = la.process_line("1.196.116.32 -  - [29/Jun/2017:03:50:23 +0300] \"GET /api/v2/banner/25023278 HTTP/1.1\" 200 924 \"-\" \"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5\" \"-\" \"1498697422-2190034393-4708-9752762\" \"dc7161be3\" 0.841")

        self.assertEqual(log['request'], request)
        self.assertEqual(log['request_time'], request_time)


if __name__ == '__main__':
    unittest.main()