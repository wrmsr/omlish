import http.server
import os
import signal
import socketserver
import subprocess
import sys
import time

import requests


PIDFILE = '/tmp/time_server.pid'
PORT = 8000
LINGER_TIME = 600  # 10 minutes in seconds


class TimeHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/time':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(time.ctime().encode())
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)


def start_server():
    with socketserver.TCPServer(('', PORT), TimeHandler) as httpd:
        print(f'Serving at port {PORT}')
        httpd.serve_forever()


def daemonize():
    # First fork
    pid = os.fork()
    if pid > 0:
        sys.exit(0)  # Exit parent process

    # Decouple from parent environment
    os.chdir('/')
    os.setsid()
    os.umask(0)

    # Second fork
    pid = os.fork()
    if pid > 0:
        sys.exit(0)  # Exit second parent process

    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = open(os.devnull)
    so = open(os.devnull, 'a+')
    se = open(os.devnull, 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    # Write PID file
    with open(PIDFILE, 'w') as f:
        f.write(str(os.getpid()))

    # Start the server
    start_server()


def ensure_server_running():
    if os.path.exists(PIDFILE):
        with open(PIDFILE) as f:
            pid = int(f.read().strip())
            try:
                os.kill(pid, 0)  # Check if the process is running
                return
            except OSError:
                os.remove(PIDFILE)  # Remove stale PID file

    # Start the server in a new process
    server_process = subprocess.Popen([sys.executable, __file__, 'serve'])
    with open(PIDFILE, 'w') as f:
        f.write(str(server_process.pid))


def get_time():
    try:
        response = requests.get(f'http://localhost:{PORT}/time')
        response.raise_for_status()
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f'Error fetching time: {e}')


def stop_server():
    if os.path.exists(PIDFILE):
        with open(PIDFILE) as f:
            pid = int(f.read().strip())
            try:
                os.kill(pid, signal.SIGTERM)
                os.remove(PIDFILE)
            except OSError as e:
                print(f'Error stopping server: {e}')


def main():
    if len(sys.argv) < 2:
        print('Usage: python time_server.py <command>')
        print('Commands: time, serve, stop')
        sys.exit(1)

    command = sys.argv[1]
    if command == 'time':
        ensure_server_running()
        get_time()
    elif command == 'serve':
        daemonize()
    elif command == 'stop':
        stop_server()
    else:
        print(f'Unknown command: {command}')
        sys.exit(1)


if __name__ == '__main__':
    main()
