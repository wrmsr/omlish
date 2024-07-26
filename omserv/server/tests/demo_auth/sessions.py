"""
TODO:
 - compress
 - 'tagged' json marshal
"""
import base64
import hashlib
import hmac
import json
import struct
import time
import typing as ta


SECRET_KEY = 'secret-key-goes-here'  # noqa
SALT = 'cookie-session'


DIGESTMOD = hashlib.sha1


def base64_encode(b: bytes) -> bytes:
    return base64.urlsafe_b64encode(b).rstrip(b'=')


def base64_decode(b: bytes) -> bytes:
    b += b'=' * (-len(b) % 4)
    return base64.urlsafe_b64decode(b)


def get_signature(key: bytes, value: bytes) -> bytes:
    mac = hmac.new(key, msg=value, digestmod=DIGESTMOD)
    return mac.digest()


def verify_signature(key: bytes, value: bytes, sig: bytes) -> bool:
    return hmac.compare_digest(sig, get_signature(key, value))


def int_to_bytes(num: int) -> bytes:
    return struct.pack('>Q', num).lstrip(b'\0')


def bytes_to_int(bytestr: bytes) -> int:
    return struct.unpack('>Q', bytestr.rjust(8, b'\0'))[0]


def load_session_cookie(signed_value: bytes) -> ta.Any:
    sep = b'.'
    value, sig = signed_value.rsplit(sep, 1)

    sig_b = base64_decode(sig)

    mac = hmac.new(SECRET_KEY.encode(), digestmod=DIGESTMOD)
    mac.update(SALT.encode())
    d_key = mac.digest()

    if not verify_signature(d_key, value, sig_b):
        raise Exception

    value, ts_bytes = value.rsplit(sep, 1)
    ts_int = bytes_to_int(base64_decode(ts_bytes))

    max_age = 31 * 24 * 60 * 60
    age = int(time.time()) - ts_int

    if age > max_age:
        raise Exception
    if age < 0:
        raise Exception

    payload = value

    if payload.startswith(b'.'):
        # payload = payload[1:]
        # decompress = True
        raise NotImplementedError('compression')

    jsrc = base64_decode(payload)

    obj = json.loads(jsrc.decode())

    return obj


def save_session_cookie(obj: ta.Any) -> bytes:
    raise NotImplementedError


def _main() -> None:
    signed_value = b'eyJfZnJlc2giOmZhbHNlfQ.ZqLLYg.4hMQ-ZLN_40k-q7efM87KEEx93g'
    obj = load_session_cookie(signed_value)
    print(obj)
    out = save_session_cookie(obj)
    print(out)


if __name__ == '__main__':
    _main()
