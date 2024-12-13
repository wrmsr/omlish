python
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import argparse
import signal
import atexit

class TimeServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/time":
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(time.ctime().encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'404 Not Found')

def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f'fork #1 failed: {e.strerror}\n')
        sys.exit(1)

    os.chdir('/')
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f'fork #2 failed: {e.strerror}\n')
        sys.exit(1)

    pidfile = '/var/run/time_server.pid'
    with open(pidfile, 'w') as f:
        print(os.getpid(), file=f)

    atexit.register(remove_pidfile, pidfile)

def remove_pidfile(pidfile):
    os.remove(pidfile)

def start_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, TimeServer)
    print(f'Started httpd on port {httpd.server_address[1]}')
    httpd.serve_forever()

def check_server():
    pidfile = '/var/run/time_server.pid'
    if os.path.exists(pidfile):
        with open(pidfile, 'r') as f:
            pid = int(f.read().strip())
        if os.path.exists(f'/proc/{pid}'):
            return True
    return False

def cli():
    parser = argparse.ArgumentParser(description='A simple time server.')
    parser.add_argument('--start', action='store_true', help='Start the server in the background.')
    parser.add_argument('--time', action='store_true', help='Print the current time from the server.')
    args = parser.parse_args()

    if args.start:
        if check_server():
            print('Server is already running.')
        else:
            daemonize()
            start_server()

    if args.time:
        if not check_server():
            print('Server is not running. Starting it...')
            daemonize()
            start_server()
        time.sleep(2)  # Wait for the server to start
        import requests
        response = requests.get('http://localhost:8000/time')
        print(response.text)

if __name__ == '__main__':
    cli()
