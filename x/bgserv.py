#!/usr/bin/env python3
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

from omlish.os.pidfile import Pidfile


PIDFILE = '/tmp/my_server.pid'
PORT = 8888
IDLE_TIMEOUT = 10 * 60  # 10 minutes in seconds

# We'll use a global variable to track the last request time in the daemon.
last_request_time = None


def is_running():
    """
    Check if the daemon (server) is already running by reading the PID file
    and sending a signal 0 to that PID.
    """
    if not os.path.isfile(PIDFILE):
        return False

    with Pidfile(PIDFILE) as pf:
        return not pf.try_lock()


def start_server_daemon():
    """
    Double-fork to daemonize the process, ensuring it detaches from the
    controlling terminal and can outlive the CLI process.
    """
    if (pid := os.fork()):  # noqa
        # Parent process returns
        return

    # First child process becomes session leader
    os.setsid()

    pid = os.fork()
    if pid > 0:
        # First child exits, second child (grandchild) is the daemon
        sys.exit(0)

    # We are now in the daemon process (grandchild).
    # Close off file descriptors if needed (stdout/stderr), but minimal example here:
    sys.stdout.flush()
    sys.stderr.flush()

    # Write daemon PID to pidfile
    with Pidfile(PIDFILE) as pf:  # noqa
        pf.write()
        run_server()


def run_server():
    """
    Run the HTTP server on localhost:PORT. The server handles only /time.
    It spawns a watcher thread that checks for idle time and shuts down
    after 10 minutes with no requests.
    """
    global last_request_time
    last_request_time = time.time()

    class TimeHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            global last_request_time
            if self.path == '/time':
                last_request_time = time.time()  # Update last request time
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'time': time.ctime(),
                    'pid': os.getpid(),
                }).encode('utf-8'))
            else:
                self.send_error(404, 'Not Found')

    httpd = HTTPServer(('127.0.0.1', PORT), TimeHandler)

    def idle_watcher():
        # Periodically check if the server is idle for more than IDLE_TIMEOUT
        while True:
            time.sleep(30)  # Check every 30 seconds
            if time.time() - last_request_time > IDLE_TIMEOUT:
                # Shutdown due to inactivity
                httpd.shutdown()
                break

    watcher_thread = threading.Thread(target=idle_watcher, daemon=True)
    watcher_thread.start()

    httpd.serve_forever()


def get_time():
    """
    CLI call for 'time' command: ensures the server is running, then
    performs a GET request to /time and prints the response.
    """
    if not is_running():
        start_server_daemon()
        # Give the daemon a moment to bind to the port
        time.sleep(1)

    # Perform the GET request to /time
    try:
        # Using only the standard library, so we can do a manual socket approach
        # or simply use urllib if allowed. urllib is part of the standard library:
        import urllib.request

        with urllib.request.urlopen(f'http://127.0.0.1:{PORT}/time') as resp:
            body = resp.read().decode('utf-8')
            print(body)
    except Exception as e:
        print(f'Error connecting to server: {e}', file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        print('Usage: python myservice.py time')
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == 'time':
        get_time()
    else:
        print(f'Unknown command: {cmd}')
        sys.exit(1)


if __name__ == '__main__':
    main()
