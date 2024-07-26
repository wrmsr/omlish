"""
TODO:
 - 'tagged' json marshal
 - expires
"""
import base64
import hashlib
import hmac
import json
import struct
import time
import typing as ta
import zlib


SECRET_KEY = 'secret-key-goes-here'  # noqa
SALT = 'cookie-session'
SEP = b'.'

DIGESTMOD = hashlib.sha1


def derive_key() -> bytes:
    mac = hmac.new(SECRET_KEY.encode(), digestmod=DIGESTMOD)
    mac.update(SALT.encode())
    return mac.digest()


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
    value, sig = signed_value.rsplit(SEP, 1)

    sig_b = base64_decode(sig)

    if not verify_signature(derive_key(), value, sig_b):
        raise Exception

    value, ts_bytes = value.rsplit(SEP, 1)
    ts_int = bytes_to_int(base64_decode(ts_bytes))

    max_age = 31 * 24 * 60 * 60
    age = int(time.time()) - ts_int

    if age > max_age:
        raise Exception
    if age < 0:
        raise Exception

    payload = value

    decompress = False
    if payload.startswith(b'.'):
        payload = payload[1:]
        decompress = True

    jb = base64_decode(payload)

    if decompress:
        jb = zlib.decompress(jb)

    obj = json.loads(jb.decode())

    return obj


def save_session_cookie(obj: ta.Any) -> bytes:
    jb = json.dumps(obj, separators=(',', ':')).encode()

    is_compressed = False
    compressed = zlib.compress(jb)

    if len(compressed) < (len(jb) - 1):
        jb = compressed
        is_compressed = True

    base64d = base64_encode(jb)

    if is_compressed:
        base64d = b'.' + base64d

    payload = base64d

    timestamp = base64_encode(int_to_bytes(int(time.time())))

    value = payload + SEP + timestamp
    return value + SEP + base64_encode(get_signature(derive_key(), value))


def _main() -> None:
    sv = b'eyJfZnJlc2giOmZhbHNlfQ.ZqLLYg.4hMQ-ZLN_40k-q7efM87KEEx93g'

    print(sv)
    for _ in range(3):
        obj = load_session_cookie(sv)
        print(obj)
        sv = save_session_cookie(obj)
        print(sv)


if __name__ == '__main__':
    _main()
