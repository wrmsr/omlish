import base64
import dataclasses as dc
import hashlib
import hmac
import struct
import time
import typing as ta
import zlib

from omlish import http as hu
from omlish import lang


##


def base64_encode(b: bytes) -> bytes:
    return base64.urlsafe_b64encode(b).rstrip(b'=')


def base64_decode(b: bytes) -> bytes:
    b += b'=' * (-len(b) % 4)
    return base64.urlsafe_b64decode(b)


def int_to_bytes(num: int) -> bytes:
    return struct.pack('>Q', num).lstrip(b'\0')


def bytes_to_int(bytestr: bytes) -> int:
    return struct.unpack('>Q', bytestr.rjust(8, b'\0'))[0]


##


class Signer:
    @dc.dataclass(frozen=True)
    class Config:
        secret_key: str = 'secret-key-goes-here'  # noqa
        salt: str = 'cookie-session'

    def __init__(self, config: Config = Config()) -> None:
        super().__init__()

        self._config = config

    @lang.cached_function
    def digest(self) -> ta.Any:
        return hashlib.sha1

    @lang.cached_function
    def derive_key(self) -> bytes:
        mac = hmac.new(self._config.secret_key.encode(), digestmod=self.digest())
        mac.update(self._config.salt.encode())
        return mac.digest()

    def get_signature(self, value: bytes) -> bytes:
        mac = hmac.new(self.derive_key(), msg=value, digestmod=self.digest())
        return mac.digest()

    def verify_signature(self, value: bytes, sig: bytes) -> bool:
        return hmac.compare_digest(sig, self.get_signature(value))


class CookieSessionStore:
    def __init__(self, signer: Signer) -> None:
        super().__init__()

        self._signer = signer

    SEP = b'.'

    def load(self, cookie: bytes) -> ta.Any:
        value, sig = cookie.rsplit(self.SEP, 1)

        sig_b = base64_decode(sig)

        if not self._signer.verify_signature(value, sig_b):
            raise Exception

        value, ts_bytes = value.rsplit(self.SEP, 1)
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

        jbs = jb.decode()

        obj = hu.JSON_TAGGER.loads(jbs)

        return obj

    def save(self, obj: ta.Any) -> bytes:
        jbs = hu.JSON_TAGGER.dumps(obj)

        jb = jbs.encode()

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

        value = payload + self.SEP + timestamp
        return value + self.SEP + base64_encode(self._signer.get_signature(value))


COOKIE_SESSION_STORE = CookieSessionStore(Signer())


def extract_session(scope) -> dict[str, ta.Any]:
    for k, v in scope['headers']:
        if k == b'cookie':
            cks = hu.parse_cookie(v.decode())  # FIXME: lol
            sk = cks.get('session')
            if sk:
                return COOKIE_SESSION_STORE.load(sk[0].encode())  # FIXME: lol
    return {}


def build_session_headers(session: ta.Mapping[str, ta.Any]) -> list[tuple[bytes, bytes]]:
    return [
        (b'Vary', b'Cookie'),
        (b'Set-Cookie', b'session=' + COOKIE_SESSION_STORE.save(session)),
    ]


def _main() -> None:
    sv = b'eyJfZnJlc2giOmZhbHNlfQ.ZqLLYg.4hMQ-ZLN_40k-q7efM87KEEx93g'

    print(sv)
    for _ in range(3):
        obj = COOKIE_SESSION_STORE.load(sv)
        print(obj)
        sv = COOKIE_SESSION_STORE.save(obj)
        print(sv)


if __name__ == '__main__':
    _main()
