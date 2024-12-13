python
import argparse
import atexit
import http.server
import os
import socketserver
import subprocess
import sys
import time

import requests


# Constants
PORT = 8000
PIDFILE = '/tmp/time_server.pid'
LINGER_TIME = 600  # 10 minutes


class TimeRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/time':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(time.strftime('%Y-%m-%d %H:%M:%S').encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')


def start_server():
    # Double-fork to daemonize the process
    try:
        pid = os.fork()
        if pid > 0:
            # Parent process, exit immediately
            sys.exit(0)
    except OSError as e:
        print(f'fork #1 failed: {e.errno} ({e.strerror})')
        sys.exit(1)

    # Decouple from parent environment
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            # Parent process, exit immediately
            sys.exit(0)
    except OSError as e:
        print(f'fork #2 failed: {e.errno} ({e.strerror})')
        sys.exit(1)

    # Write pid to pidfile
    with open(PIDFILE, 'w') as f:
        f.write(str(os.getpid()))

    # Start the server
    with socketserver.TCPServer(('', PORT), TimeRequestHandler) as httpd:
        print(f'Server started on port {PORT}')
        httpd.serve_forever()


def stop_server():
    try:
        with open(PIDFILE) as f:
            pid = int(f.read())
        os.kill(pid, 9)
        os.remove(PIDFILE)
    except FileNotFoundError:
        pass


def get_time():
    try:
        response = requests.get(f'http://localhost:{PORT}/time')
        return response.text.strip()
    except requests.ConnectionError:
        # If the server is not running, start it
        start_server_in_background()
        # Wait for the server to start
        time.sleep(1)
        return get_time()


def start_server_in_background():
    # Check if the server is already running
    try:
        with open(PIDFILE) as f:
            pid = int(f.read())
        if os.kill(pid, 0) == 0:
            # Server is already running, do nothing
            return
    except FileNotFoundError:
        pass
    except OSError:
        # Server is not running, start it
        pass

    # Start the server in the background
    subprocess.Popen([sys.executable, __file__, 'start-server'])


def main():
    parser = argparse.ArgumentParser(description='Time server CLI')
    subparsers = parser.add_subparsers(dest='command')

    time_parser = subparsers.add_parser('time', help='Get the current time')
    start_server_parser = subparsers.add_parser(
        'start-server', help='Start the time server',
    )

    args = parser.parse_args()

    if args.command == 'time':
        print(get_time())
    elif args.command == 'start-server':
        start_server()
    else:
        parser.print_help()


if __name__ == '__main__':
    atexit.register(stop_server)
    main()
