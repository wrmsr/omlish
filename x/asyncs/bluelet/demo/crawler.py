"""
Demonstrates various ways of writing an application that makes many URL requests.

Unfortunately, because the Python standard library only includes blocking HTTP libraries, taking advantage of
asynchronous I/O currently entails writing a custom HTTP client. This example includes a very simple, GET-only HTTP
requester.
"""
import json
import multiprocessing
import threading
import time
from urllib.parse import urlparse
from urllib.request import urlopen

from .. import bluelet as bl


# URL = 'https://api.github.com/args/%s/results/latest'
# ARGS = [
#     'pytorch/pytorch',
#     'tinygrad/tinygrad',
#     'numpy/numpy',
#     'agronholm/anyio',
#     'astral-sh/ruff',
#     'indygreg/python-build-standalone',
# ]

URL = 'https://httpbingo.org/%s'
ARGS = [
    'get?foo=bar',
    'get?baz=qux',
    'user-agent',
    'uuid',
]


class AsyncHttpClient:
    """A basic Bluelet-based asynchronous HTTP client. Only supports very simple GET queries."""

    def __init__(self, host: str, port: int, path: str) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.path = path

    def headers(self) -> bytes:
        """Returns the HTTP headers for this request."""
        heads = [
            f'GET {self.path} HTTP/1.1',
            f'Host: {self.host}',
            'User-Agent: bl-example',
        ]
        return '\r\n'.join(heads).encode('utf8') + b'\r\n\r\n'

    # Convenience methods.

    @classmethod
    def from_url(cls, url: str) -> 'AsyncHttpClient':
        """Construct a request for the specified URL."""
        res = urlparse(url)
        path = res.path
        if res.query:
            path += '?' + res.query
        return cls(res.hostname, res.port or 80, path)

    @classmethod
    def fetch(cls, url: str) -> bl.Coro:
        """Fetch content from an HTTP URL. This is a coroutine suitable for yielding to bl."""
        client = cls.from_url(url)
        yield client._connect()
        yield client._request()
        status, headers, body = yield client._read()
        yield bl.end(body)

    # Internal coroutines.

    def _connect(self) -> bl.Coro:
        self.conn = yield bl.connect(self.host, self.port)

    def _request(self) -> bl.Coro:
        yield self.conn.sendall(self.headers())

    def _read(self) -> bl.Coro:
        buf = []
        while True:
            data = yield self.conn.recv(4096)
            if not data:
                break
            buf.append(data)
        response = ''.join(buf)

        # Parse response.
        headers, body = response.split('\r\n\r\n', 1)
        headers = headers.split('\r\n')
        status = headers.pop(0)
        version, code, message = status.split(' ', 2)
        headervals = {}
        for header in headers:
            key, value = header.split(': ')
            headervals[key] = value

        yield bl.end((int(code), headers, body))


# Various ways of writing the crawler.


def run_bl():
    # No lock is required guarding the shared variable because only one thread is actually running at a time.
    results = {}

    def fetch(arg: str) -> bl.Coro:
        url = URL % arg
        data = yield AsyncHttpClient.fetch(url)
        results[arg] = json.loads(data)

    def crawl() -> bl.Coro:
        for arg in ARGS:
            yield bl.spawn(fetch(arg))

    bl.run(crawl())
    return results


def run_sequential():
    results = {}

    for arg in ARGS:
        url = URL % arg
        f = urlopen(url)
        data = f.read().decode('utf8')
        results[arg] = json.loads(data)

    return results


def run_threaded():
    # We need a lock to avoid conflicting updates to the results dictionary.
    lock = threading.Lock()
    results = {}

    class Fetch(threading.Thread):
        def __init__(self, arg):
            threading.Thread.__init__(self)
            self.arg = arg

        def run(self):
            url = URL % self.arg
            f = urlopen(url)
            data = f.read().decode('utf8')
            result = json.loads(data)
            with lock:
                results[self.arg] = result

    # Start every thread and then wait for them all to finish.
    threads = [Fetch(arg) for arg in ARGS]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return results


def _process_fetch(arg):
    # Mapped functions in multiprocessing can't be closures, so this has to be at the module-global scope.
    url = URL % arg
    f = urlopen(url)
    data = f.read().decode('utf8')
    result = json.loads(data)
    return (arg, result)


def run_processes(ctx: multiprocessing.context.BaseContext | None = None):
    if ctx is not None:
        pool = ctx.Pool(len(ARGS))
    else:
        pool = multiprocessing.Pool(len(ARGS))
    result_pairs = pool.map(_process_fetch, ARGS)
    return dict(result_pairs)


# Main driver.


def _main() -> None:
    strategies = {
        # 'bl': run_bl,
        'sequential': run_sequential,
        'threading': run_threaded,
        'multiprocessing': run_processes,
    }
    for name, func in strategies.items():
        start = time.time()
        results = func()
        end = time.time()
        print(f'{name}: {end - start:.2f} seconds')

    print()

    # Show the results, just for fun.
    # for username, tweet in results.items():  # noqa
    #     print(f'{username}: {tweet}')


if __name__ == '__main__':
    _main()
