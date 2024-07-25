import base64
import hashlib
import hmac


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


if __name__ == '__main__':
    _main()
