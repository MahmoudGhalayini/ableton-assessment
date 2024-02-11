# Copyright 2024 Ableton
# All rights reserved


from http.server import HTTPServer
from core.service_handler import ServiceRequestHandler
import threading


def run_server(server_class=HTTPServer, handler_class=ServiceRequestHandler, port=5000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    return httpd


class ServerThread(threading.Thread):
    def __init__(self, httpd):
        super().__init__()
        self.httpd = httpd

    def run(self):
        self.httpd.serve_forever()

    def stop_server(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        print('Server stopped.')


def run(port):
    httpd = run_server(port=port)
    if __name__ == '__main__':
        print(f'Starting server on port {httpd.server_port}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        print('Server stopped.')
    else:
        return httpd


if __name__ == '__main__':
    run(port=5000)
