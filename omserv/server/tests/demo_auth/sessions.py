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


def _main() -> None:
    secret_key = 'secret-key-goes-here'
    salt = 'cookie-session'

    signed_value = b'eyJfZnJlc2giOmZhbHNlfQ.ZqLLYg.4hMQ-ZLN_40k-q7efM87KEEx93g'
    sep = b'.'
    value, sig = signed_value.rsplit(sep, 1)

    def base64_decode(string: str | bytes) -> bytes:
        string += b"=" * (-len(string) % 4)
        return base64.urlsafe_b64decode(string)

    sig_b = base64_decode(sig)

    digestmod = hashlib.sha1

    mac = hmac.new(secret_key.encode(), digestmod=digestmod)
    mac.update(salt.encode())
    d_key = mac.digest()

    def get_signature(key: bytes, value: bytes) -> bytes:
        mac = hmac.new(key, msg=value, digestmod=digestmod)
        return mac.digest()

    def verify_signature(key: bytes, value: bytes, sig: bytes) -> bool:
        return hmac.compare_digest(sig, get_signature(key, value))

    if not verify_signature(d_key, value, sig_b):
        raise Exception

    def int_to_bytes(num: int) -> bytes:
        return struct.pack('>Q', num).lstrip(b'\0')

    def bytes_to_int(bytestr: bytes) -> int:
        return struct.unpack('>Q', bytestr.rjust(8, b'\0'))[0]

    value, ts_bytes = value.rsplit(sep, 1)
    ts_int = bytes_to_int(base64_decode(ts_bytes))

    max_age = 31 * 24 * 60 * 60
    age = int(time.time()) - ts_int

    if age > max_age:
        raise Exception
    if age < 0:
        raise Exception

    payload = value

    # if payload.startswith(b'.'):
    #     payload = payload[1:]
    #     decompress = True

    jsrc = base64_decode(payload)

    obj = json.loads(jsrc.decode())

    print(obj)


if __name__ == '__main__':
    _main()
