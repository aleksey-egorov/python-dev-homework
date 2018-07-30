#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime
import os
from optparse import OptionParser
from socket import *

class SimpleHttpServer():
    timeout = None

    def __init__(self, server_address, handler, worker=1, doc_root='./htdocs/', activate=True):
        """Constructor"""

        self.server_address = server_address
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.RequestHandler = handler
        self.worker = worker
        self.doc_root = doc_root

        self.__shutdown_request = False
        self.__is_working = False
        self.allow_reuse_address = False
        self.request_queue_size = 5

        if activate:
            self.bind_server()
            self.activate_server()

    def serve_forever(self, poll_interval=0.5):
        """Handle one request at a time until shutdown.
        Polls for shutdown every poll_interval seconds. Ignores
        self.timeout. If you need to do periodic tasks, do them in
        another thread.
        """
        self.__is_working = False
        try:
            while not self.__shutdown_request:
                # XXX: Consider using another file descriptor or
                # connecting to the socket to wake this up instead of
                # polling. Polling reduces our responsiveness to a
                # shutdown request and wastes cpu at all other times.
               # r, w, e = _eintr_retry(select.select, [self], [], [],
                #                       poll_interval)

                self._handle_request_noblock()
        finally:
            self.__shutdown_request = False
            self.__is_working = True

    def shutdown(self):
        """Stops the serve_forever loop.
        Blocks until the loop has finished. This must be called while
        serve_forever() is running in another thread, or it will
        deadlock.
        """
        self.__shutdown_request = True
        self.__is_working = False

    # The distinction between handling, getting, processing and
    # finishing a request is fairly arbitrary.  Remember:
    #
    # - handle_request() is the top-level call.  It calls
    #   select, get_request(), verify_request() and process_request()
    # - get_request() is different for stream or datagram sockets
    # - process_request() is the place that may fork a new process
    #   or create a new thread to finish the request
    # - finish_request() instantiates the request handler class;
    #   this constructor will handle the request all by itself


    def _handle_request_noblock(self):
        """Handle one request, without blocking.
        I assume that select.select has returned that the socket is
        readable before this function was called, so there should be
        no risk of blocking in get_request().
        """
        try:
            request, client_address = self.get_request()
        except Exception as err:
            print ("ERROR=", type(err), err)
            time.sleep(10)
            return
        if self.verify_request(request, client_address):
            #try:
            self.process_request(request, client_address)
            #except Exception as err:
            #    print ("ERR EX=", type(err), err)
            #    self.handle_error(request, client_address)
            #    self.shutdown_request(request)
        else:
            self.shutdown_request(request)

    def bind_server(self):
        """Called by constructor to bind the socket.
        May be overridden.
        """
        if self.allow_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()

    def activate_server(self):
        """Called by constructor to activate the server.
        May be overridden.
        """
        self.socket.listen(self.request_queue_size)
        logging.info("Server is active ...")

    def close_server(self):
        """Called to clean-up the server.
              May be overridden.
              """
        self.socket.close()
        logging.info("Server is closed")

    def get_request(self):
        """Get the request and client address from the socket.
        May be overridden.
        """
        return self.socket.accept()

    def verify_request(self, request, client_address):
        return True

    def process_request(self, request, client_address):
        """Call finish_request.
        Overridden by ForkingMixIn and ThreadingMixIn.
        """
        self.RequestHandler(request, client_address, self)
        self.shutdown_request(request)

    #def finish_request(self, request, client_address):
        #"""Finish one request by instantiating RequestHandlerClass."""
        #self.RequestHandler(request, client_address, self)

    def shutdown_request(self, request):
        """Called to shutdown and close an individual request."""
        try:
            # explicitly shutdown.  socket.close() merely releases
            # the socket and waits for GC to perform the actual close.
            request.shutdown(SHUT_WR)
            logging.info("Request is shut down")
        except Exception as err:
            print("ERROR=", type(err), err)
            pass  # some platforms may raise ENOTCONN here
        self.close_request(request)

    def close_request(self, request):
        """Called to clean up an individual request."""
        request.close()
        logging.info("Request is closed")

    def handle_error(self, request, client_address):
        print ("HANDLE ERROR=", request, client_address)
        #print ("ERROR=", self.socket.error)



class SimpleHttpHandler():
    def __init__(self, request, client_address, server):

        self.client_address = client_address
        self.server = server

        self.req_handler = SimpleRequestHandler(request, server)
        resp_content = self.req_handler.process_request()
        print ("RESPONSE=", resp_content)

        self.resp_handler = SimpleResponseHandler(request, resp_content)
        result = self.resp_handler.send_response()
        print("RESULT=", result)


class SimpleRequestHandler():

    def __init__(self, request, server):
        self.allowed_methods = ['GET', 'HEAD', 'POST']
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
                'url': parts[1],
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
                    raise

    def parse_url(self, url):
        print ('parsing url:', url)
        return url.split("/")

    def do_post(self):
        print ("POST:", self.data)
        print ("root: ", self.server.doc_root)

        return '123'

    def do_get(self):
        print ("GET:", self.data)
        url_parts = self.parse_url(self.headers['url'])
        content = self.get_content(url_parts)

        print ("ct=", content)

        return content

    def get_content(self, url_parts):
        path = os.path.join(self.server.doc_root, *url_parts)
        print("PATH=", path)
        if os.path.exists(path):
            if os.path.isdir(path):
                path = os.path.join(path, 'index.html')

            try:
                content = open(path, 'r').read()
                return content
            except:
                pass



class SimpleResponseHandler():

    def __init__(self, request, content):
        self.request = request
        self.content = str(content)
        self.protocol = 'HTTP/1.1'
        self.content_type = ''

    def send_response(self):
        headers_str = self.make_headers()

        self.response_code = '200'

        response = self.protocol + ' ' + self.response_code + "\r\n"
        response += headers_str + "\r\n"
        response += self.content

        print("FINAL RESP: ", response)
        self.request.send(response.encode("utf-8"))

    def make_headers(self):
        headers = {
             'Date': datetime.datetime.now(),
             'Server': 'simple-http-server',
             'Content-Length': len(self.content),
             'Content-Type': self.content_type,
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

    server = SimpleHttpServer(("localhost", opts.port), handler=SimpleHttpHandler, worker=opts.worker, doc_root=opts.root)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.close_server()
