"""
FIXME: jettison wsgiref?
"""
import asyncio

import httptools


"""
base:
    def get_http_version(self):

    def should_keep_alive(self):

    def should_upgrade(self):

    def feed_data(self, data):

request:
    def get_method(self):

response
    def get_status_code(self):
"""


class HttpToolsRequestParserListener:

    def on_message_begin(self):
        pass

    def on_url(self, url: bytes):
        pass

    def on_header(self, name: bytes, value: bytes):
        pass

    def on_headers_complete(self):
        pass

    def on_body(self, body: bytes):
        pass

    def on_message_complete(self):
        pass

    def on_chunk_header(self):
        pass

    def on_chunk_complete(self):
        pass

    def on_status(self, status: bytes):
        pass


# https://github.com/MagicStack/httptools/issues/20


class Request(HttpToolsRequestParserListener):

    def __init__(self):
        super().__init__()

        self.EOF = False

    def on_url(self, url: bytes):
        self.on_url_called = True

    def on_message_complete(self):
        self.EOF = True


async def serve(reader, writer):
    chunks = 2 ** 16
    req = Request()
    parser = httptools.HttpRequestParser(req)
    while True:
        data = await reader.read(chunks)
        parser.feed_data(data)
        if not data or req.EOF:
            break
    assert req.on_url_called
    writer.write(b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK')
    writer.write_eof()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = loop.create_task(asyncio.start_server(serve, '127.0.0.1', 8080))
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Bye.')
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
