"""
"""
import os
import sys
import time
import atexit
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Configuration
HOST = "127.0.0.1"
PORT = 8080
PIDFILE = "/tmp/simple_http_server.pid"
INACTIVITY_TIMEOUT = 600  # 10 minutes

# HTTP request handler
class TimeRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/time":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S").encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress logging to the console


# Daemonize the process
def daemonize():
    if os.fork() > 0:
        sys.exit(0)  # Exit parent process
    os.setsid()  # Create a new session
    if os.fork() > 0:
        sys.exit(0)  # Exit second parent process

    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    with open("/dev/null", "r") as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open("/dev/null", "a+") as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())

    # Write PID to file
    with open(PIDFILE, "w") as f:
        f.write(str(os.getpid()) + "\n")

    # Register cleanup
    atexit.register(lambda: os.remove(PIDFILE))


# Start the server
def start_server():
    def timeout_check(httpd):
        while True:
            time.sleep(1)
            if time.time() - httpd.last_request_time > INACTIVITY_TIMEOUT:
                print("Server inactive. Shutting down.")
                os._exit(0)

    server = HTTPServer((HOST, PORT), TimeRequestHandler)
    server.last_request_time = time.time()

    # Start timeout check thread
    import threading
    threading.Thread(target=timeout_check, args=(server,), daemon=True).start()

    print(f"Server running at http://{HOST}:{PORT}")
    server.serve_forever()


# Check if the server is already running
def is_server_running():
    if os.path.exists(PIDFILE):
        try:
            with open(PIDFILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # Check if the process is running
            return True
        except (ValueError, OSError):
            pass
    return False


# CLI entry point
def cli():
    if is_server_running():
        print(f"Server is already running at http://{HOST}:{PORT}.")
        sys.exit(0)

    print("Starting server as a background daemon...")
    daemonize()
    start_server()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        # Stop the server
        if is_server_running():
            with open(PIDFILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 15)
            print("Server stopped.")
        else:
            print("Server is not running.")
    else:
        cli()
