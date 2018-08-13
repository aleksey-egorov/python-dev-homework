#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime
import os
import re
import mimetypes
import multiprocessing

from optparse import OptionParser
from socket import socket, AF_INET, SOCK_STREAM, SHUT_WR
from urllib.parse import unquote

valid_url_part = re.compile(r'([a-xzA-Z0-9\=\+\-\_\.\,]*?)')
bad_url_exceptions = ['..', 'etc', 'passwd']


class SimpleHttpServer():
    timeout = None

    def __init__(self, server_address, handler, doc_root='./htdocs/', activate=True):

        self.server_address = server_address
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.request_handler = handler
        self.doc_root = doc_root

        self.__shutdown_request = False
        self.__is_working = False
        self.request_queue_size = 5

        if activate:
            self.bind_server()
            self.activate_server()

    def serve_forever(self):
        self.__is_working = False
        try:
            while not self.__shutdown_request:
                self.__is_working = True
                self._handle_request_noblock()
        finally:
            self.__shutdown_request = False
            self.__is_working = False

    def _handle_request_noblock(self):
        try:
            conn, client_address = self.get_connection()
            logging.info("Recieved request from {}".format(client_address))
        except Exception as err:
            logging.error("Error getting request: {}".format(err))
            return
        try:
            self.process_request(conn, client_address)
        except Exception as err:
            logging.error("Error processing request: {}".format(err))
        finally:
            self.shutdown_request(conn)

    def bind_server(self):
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()

    def activate_server(self):
        self.socket.listen(self.request_queue_size)
        logging.info("Server is active ...")

    def close_server(self):
        self.socket.close()
        logging.info("Server is closed")

    def get_connection(self):
        accept = self.socket.accept()
        return accept

    def process_request(self, conn, client_address):
        self.request_handler(conn, client_address, self)

    def shutdown_request(self, conn):
        try:
            conn.shutdown(SHUT_WR)
            logging.info("Request is shut down")
        except Exception as err:
            logging.error("Error shutting down request: {} request={}".format(err, conn))
            pass  # some platforms may raise ENOTCONN here
        finally:
            self.close_request(conn)

    def close_request(self, conn):
        conn.close()
        logging.info("Request is closed")


class SimpleRequestHandler():

    def __init__(self, conn, client_address, server, process=True):
        self.allowed_methods = ['GET', 'HEAD']
        self.conn = conn
        self.client_address = client_address
        self.server = server
        self.headers = {}

        if process:
            content = self.process_request()
            result = self.make_response(conn, content)

    def process_request(self):
        self.read_request()
        self.parse_headers()
        return self.handle_request()

    def read_request(self):
        data = bytes()
        buf_size = 1024
        while True:
            chunk = self.conn.recv(buf_size)
            data += chunk
            if len(chunk) < buf_size:
                break
        data = data.strip()
        self.data = data.decode("utf-8")

    def parse_headers(self):
        headers_parts = self.data.split("\r\n")
        try:
            parts =  headers_parts[0].split(" ")
            self.headers = {
                'method': parts[0],
                'url': unquote(parts[1]),
                'protocol': parts[2]
            }
        except:
            logging.info("Request format is invalid")
        try:
            for pt in headers_parts[1:]:
                key, val = pt.split(": ")
                self.headers[key] = val
        except:
            pass

    def handle_request(self):
        if "method" in self.headers:
            if self.headers["method"] in self.allowed_methods:
                try:
                    method = self.__getattribute__('do_' + self.headers["method"].lower())
                    return method()
                except:
                    pass
        return {'code': 405}

    def parse_url(self, url):
        parts = url.split("/")
        query_params = ""
        if "?" in parts[-1]:
            fname, query_params = parts[-1].split("?")
            parts[-1] = fname
        for part in parts:
            if not valid_url_part.match(part) or part in bad_url_exceptions:
                return None, None
        return parts, query_params

    def do_head(self):
        url_parts, query_params = self.parse_url(self.headers['url'])
        content = self.get_content(url_parts)
        content['body'] = None
        return content

    def do_get(self):
        url_parts, query_params = self.parse_url(self.headers['url'])
        return self.get_content(url_parts)

    def get_content(self, url_parts):
        if url_parts == None:
            return {'code': 400}
        path = os.path.join(self.server.doc_root, *url_parts)
        if os.path.exists(path):
            if os.path.isdir(path):
                path = os.path.join(path, 'index.html')
            try:
                body = bytes()
                with open(path, 'rb') as file:
                    while True:
                        chunk = file.read(4096)
                        if not chunk:
                            break
                        body += chunk

                content = {
                    'body': body,
                    'length': os.path.getsize(path),
                    'type': mimetypes.guess_type(path)[0],
                    'code': 200
                }
                return content
            except Exception as err:
                logging.error("Error getting request content: {}".format(err))
        return {'code': 404}

    def make_response(self, conn, content):
        resp_handler = SimpleResponseHandler(conn, content)
        result = resp_handler.send_response()
        logging.info("Response result: code={}, body_length={}, content_type={}, send={}".format(
            resp_handler.content['code'],
            resp_handler.content['length'],
            resp_handler.content['type'], result))


class SimpleResponseHandler():

    def __init__(self, conn, content):
        self.conn = conn
        self.content = {}
        self.protocol = 'HTTP/1.1'

        self.statuses = {
            200: ('OK', 'Request complete, response send'),
            400: ('Bad Request',
                  'Bad request syntax'),
            403: ('Forbidden',
                  'Request forbidden'),
            404: ('Not Found', 'Document not found by given URI'),
            405: ('Method Not Allowed',
                  'Specified method is invalid'),
        }
        self.check_content(content)

    def check_content(self, content):
        for key in ['body', 'code', 'length', 'type']:
            if key in content:
                self.content[key] = content[key]
            else:
                self.content[key] = None

    def get_status(self):
        try:
            return self.statuses[self.content['code']][0]
        except:
            return ''

    def send_response(self):
        headers_str = self.make_headers()

        headers = self.protocol + ' ' + str(self.content['code']) + ' ' + self.get_status() + "\r\n"
        headers += headers_str + "\r\n"
        headers = headers.encode("utf-8")

        body = self.content['body']
        if body == None:
            body = bytes()
        elif isinstance(body, str):
            body = body.encode("utf-8")

        response = headers + body
        try:
            self.conn.sendall(response)
            return True
        except Exception as err:
            logging.error("Error while sending response: {}".format(err))
            return False

    def make_headers(self):
        headers = {
             'Date': datetime.datetime.now(),
             'Server': 'simple-http-server',
             'Content-Length': self.content['length'],
             'Content-Type': self.content['type'],
             'Connection': 'keep-alive'
        }
        return ''.join(["%s: %s\r\n" % (key, headers[key]) for key in headers.keys()])


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("-w", "--worker", action="store", default=1)
    op.add_option("-r", "--root", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    logging.info("Starting server at %s" % opts.port)

    server = SimpleHttpServer(("localhost", opts.port), handler=SimpleRequestHandler, doc_root=opts.root)
    def run_server():
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        except Exception as err:
            logging.error("Error starting server: {}".format(err))
        finally:
            server.close_server()

    for wrk in range(int(opts.worker)):
        logging.info("Starting worker {}".format(wrk))
        p = multiprocessing.Process(target=run_server)
        p.start()



