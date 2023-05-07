import datetime
import socket as sock
import time
import typing as ta
import wsgiref.handlers
import wsgiref.simple_server

from .. import check


def format_date(when: datetime.datetime = None) -> str:
    if when is None:
        when = datetime.datetime.now()
    return wsgiref.handlers.format_date_time(time.mktime(when.timetuple()))


def read_scgi_headers(socket: sock.socket) -> ta.Dict[bytes, bytes]:
    header_size = 0
    while True:
        char = socket.recv(1)
        if char == b':':
            break
        header_size = (header_size * 10) + int(char)
    check.state(header_size > 0)
    header_buf = socket.recv(header_size + 1)
    check.state(header_buf[-2:] == b'\0,')
    header_items = header_buf[:-2].split(b'\0')
    check.state(len(header_items) % 2 == 0)
    return dict(zip(header_items[::2], header_items[1::2]))
