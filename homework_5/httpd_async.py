#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime
import os
import mimetypes
import multiprocessing
import asyncore_epoll as asyncore
import asynchat

from optparse import OptionParser
import socket
from urllib.parse import unquote

class SimpleHttpServer(asyncore.dispatcher):
    timeout = None

    def __init__(self, server_address, handler, worker=1, doc_root='./htdocs/', activate=True):
        super().__init__()

        if not hasattr(socket, 'SO_REUSEPORT'):
            socket.SO_REUSEPORT = 15

        self.server_address = server_address
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.RequestHandler = handler
        self.worker = worker
        self.doc_root = doc_root

        self.__shutdown_request = False
        self.__is_working = False
        self.request_queue_size = 5

        if activate:
            self.bind_server()
            self.activate_server()

    def handle_accept(self):
        try:
            request, client_address = self.accept()
            logging.info("Recieved request from {}".format(client_address))
        except Exception as err:
            logging.error("Error getting request: {}".format(err))
            return
        try:
            self.process_request(request, client_address)
        except Exception as err:
            logging.error("Error processing request: {}".format(err))
        finally:
            self.shutdown_request(request)

    def handle_close(self):
        logging.info("Handle close")

    def serve_forever(self):
        self.__is_working = False
        try:
            while not self.__shutdown_request:
                self.__is_working = True
                try:
                    asyncore.loop(timeout=1, use_poll=True, poller=asyncore.epoll_poller)
                except OSError as err:
                    logging.error("Error asyncore: {}".format(err))
        finally:
            self.__shutdown_request = False
            self.__is_working = False

   # def shutdown(self):
   #     self.__shutdown_request = True
   #     self.__is_working = False

    def bind_server(self):
        logging.info("Bind: %s" % str(self.server_address))
        self.bind(self.server_address)
        self.server_address = self.getsockname()

    def activate_server(self):
        self.listen(self.request_queue_size)
        logging.info("Server is active ...")

    def close_server(self):
        self.close()
        logging.info("Server is closed")

    def process_request(self, request, client_address):
        self.RequestHandler(request, client_address, self)
        self.shutdown_request(request)

    def shutdown_request(self, request):
        try:
            request.shutdown(socket.SHUT_WR)
            logging.info("Request is shut down")
        except Exception as err:
            logging.error("Error shutting down request: {} request={}".format(err, request))
            pass  # some platforms may raise ENOTCONN here
        finally:
            self.close_request(request)

    def close_request(self, request):
        self.handle_close()
        logging.info("Request is closed")


class SimpleHttpHandler_new(asynchat.async_chat):
    def __init__(self, request, client_address, server):
        #super().__init__(sock=request)
        asynchat.async_chat.__init__(self, sock=request)

        self.client_address = client_address
        self.server = server
        self.set_terminator(b"\r\n\r\n")

    def collect_incoming_data(self, data):
        self._collect_incoming_data(data)

    def found_terminator(self):
        logging.info("foun term")
        self.process_request()

    def process_request(self):
        request = self._get_data()
        self.req_handler = SimpleRequestHandler(request, server)
        content = self.req_handler.process_request()

        self.resp_handler = SimpleResponseHandler(request, content)
        result = self.resp_handler.send_response()
        logging.info("Response result: code={}, body_length={}, content_type={}, send={}".format(
            self.resp_handler.content['code'],
            self.resp_handler.content['length'],
            self.resp_handler.content['type'], result))


class SimpleHttpHandler():
    def __init__(self, request, client_address, server):

        self.client_address = client_address
        self.server = server
        self.reading_headers = True

        self.req_handler = SimpleRequestHandler(request, server)
        content = self.req_handler.process_request()

        self.resp_handler = SimpleResponseHandler(request, content)
        result = self.resp_handler.send_response()
        logging.info("Response result: code={}, body_length={}, content_type={}, send={}".format(self.resp_handler.content['code'],
                                                                                                 self.resp_handler.content['length'],
                                                                                                 self.resp_handler.content['type'], result))

class SimpleRequestHandler():

    def __init__(self, request, server):
        self.allowed_methods = ['GET', 'HEAD']
        self.request = request
        self.server = server
        self.headers = {}

    def process_request(self):
        self.read_request()
        self.parse_headers()
        return self.handle_request()

    def read_request(self):
        data = self.request.recv(1024)
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
        bad_parts = ['..', 'etc', 'passwd']
        parts = url.split("/")
        query_params = ""
        if "?" in parts[-1]:
            fname, query_params = parts[-1].split("?")
            parts[-1] = fname
        for part in parts:
            if part in bad_parts:
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


class SimpleResponseHandler():

    def __init__(self, request, content):
        self.request = request
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
            self.request.send(response)
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

    server = SimpleHttpServer(("localhost", opts.port), handler=SimpleHttpHandler, worker=opts.worker,
                              doc_root=opts.root)
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



