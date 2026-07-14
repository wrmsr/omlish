import typing as ta


##


REQUIRED_HTTP_HEADERS: ta.Mapping[bytes, bytes] = {
    b'User-Agent': b'python-httpx/0.28.1',  # required or it 403's lol
}
