"""
Demonstrates various ways of writing an application that makes many URL requests.

Unfortunately, because the Python standard library only includes blocking HTTP libraries, taking advantage of
asynchronous I/O currently entails writing a custom HTTP client. This example includes a very simple, GET-only HTTP
requester.
"""
import functools
import json
import multiprocessing as mp
import threading
import time
import typing as ta
import urllib.parse
import urllib.request

from .. import bluelet as bl


##


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


##


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
        res = urllib.parse.urlparse(url)
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


def run_bl() -> dict[str, ta.Any]:
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


def run_seq() -> dict[str, ta.Any]:
    results = {}

    for arg in ARGS:
        url = URL % arg
        f = urllib.request.urlopen(url)
        data = f.read().decode('utf8')
        results[arg] = json.loads(data)

    return results


def run_thrd() -> dict[str, ta.Any]:
    # We need a lock to avoid conflicting updates to the results dictionary.
    lock = threading.Lock()
    results = {}

    def fetch(arg: str) -> None:
        url = URL % arg
        f = urllib.request.urlopen(url)
        data = f.read().decode('utf8')
        result = json.loads(data)
        with lock:
            results[arg] = result

    # Start every thread and then wait for them all to finish.
    threads = [
        threading.Thread(target=functools.partial(fetch, arg))
        for arg in ARGS
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return results


def _process_fetch(arg: str) -> tuple[str, ta.Any]:
    # Mapped functions in mp can't be closures, so this has to be at the module-global scope.
    url = URL % arg
    f = urllib.request.urlopen(url)
    data = f.read().decode('utf8')
    result = json.loads(data)
    return (arg, result)


def run_mp(ctx: mp.context.BaseContext | None = None) -> dict[str, ta.Any]:
    if ctx is not None:
        pool = ctx.Pool(len(ARGS))
    else:
        pool = mp.Pool(len(ARGS))
    result_pairs = pool.map(_process_fetch, ARGS)
    return dict(result_pairs)


# Main driver.


def _main() -> None:
    strategies = {
        # 'bl': run_bl,
        'seq': run_seq,
        'thrd': run_thrd,
        'mp': run_mp,
        'mp_fork': lambda: run_mp(mp.get_context('fork')),
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
