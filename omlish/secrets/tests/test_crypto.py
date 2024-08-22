import hashlib
import pytest
import secrets

from .. import crypto
from ..subprocesses import pipe_fd_subprocess_file_input
from ..subprocesses import temp_subprocess_file_input

from cryptography.hazmat.primitives import ciphers as cry_ciphs
from cryptography.hazmat.primitives.ciphers import algorithms as cry_algs
from cryptography.hazmat.primitives.ciphers import modes as cry_modes


class OpensslAes265CbcPbkdf2:
    def __init__(
            self,
            *,
            iters: int = 10_000,
    ) -> None:
        super().__init__()
        self._iters = iters

    block_size = 16
    key_length = 32
    iv_length = 16
    salt_length = 8
    prefix = b'Salted__'

    def _make_cipher(self, key: bytes, salt: bytes) -> 'cry_ciphs.Cipher':
        dk = hashlib.pbkdf2_hmac(
            'sha256',
            key,
            salt,
            self._iters,
            self.key_length + self.iv_length,
        )

        return cry_ciphs.Cipher(
            cry_algs.AES256(dk[:self.key_length]),
            cry_modes.CBC(dk[self.key_length:]),
        )

    def encrypt(self, data: bytes, key: bytes, *, salt: bytes | None = None) -> bytes:
        if salt is None:
            salt = secrets.token_bytes(self.salt_length)
        else:
            if len(salt) != self.salt_length:
                raise Exception('bad salt length')

        cipher = self._make_cipher(key, salt)

        ct = encryptor.update(b"a secret message") + encryptor.finalize()

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        if not data.startswith(self.prefix):
            raise Exception('bad prefix')

        salt = data[len(self.prefix):self.block_size]
        cipher = self._make_cipher(key, salt)

        decryptor = cipher.decryptor()
        dec = decryptor.update(data[self.block_size:]) + decryptor.finalize()

        last_byte = dec[-1]
        if last_byte > self.block_size:
            raise Exception('bad padding')

        return dec[:-last_byte]


@pytest.mark.parametrize('sec', [
    crypto.OpensslSubprocessCrypto(file_input=temp_subprocess_file_input),  # noqa
    crypto.OpensslSubprocessCrypto(file_input=pipe_fd_subprocess_file_input),  # noqa
])
def test_openssl_subproc_crypto(sec: crypto.Crypto) -> None:
    # key = sec.generate_key()
    key = b'password'

    raw = b'hello\n'
    enc = sec.encrypt(raw, key)
    enc2 = b'Salted__\xf9\x95\xd1\xd5\xdc6\x04\x8f\xa3G`%\x83\x0f\x9d]\x0bmZX6i\xb1B'

    ##

    # # def derive_key_and_iv(password, salt, key_length, iv_length):
    # #     d = d_i = ''
    # #     while len(d) < key_length + iv_length:
    # #         d_i = md5(d_i + password + salt).digest()
    # #         d += d_i
    # #     return , dk[key_length:key_length + iv_length]

    # # key, iv = derive_key_and_iv(password, salt, key_length, bs)
    # # cipher = AES.new(key, AES.MODE_CBC, iv)
    # # next_chunk = ''
    # # finished = False
    # # while not finished:
    # #     chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
    # #     if len(next_chunk) == 0:
    # #         padding_length = ord(chunk[-1])
    # #         chunk = chunk[:-padding_length]
    # #         finished = True
    # #     out_file.write(chunk)

    # last_byte = block_size - (len(enc) % block_size)
    # enc += bytes([last_byte] * last_byte)

    # https://github.com/openssl/openssl/blob/3c1713aeed4dc7d1ac25e9e365b8bd98afead638/apps/enc.c#L555-L573

    import hashlib

    block_size = 16
    key_length = 32
    iv_length = 16
    salt = enc[len('Salted__'):block_size]
    # https://stackoverflow.com/a/58824167
    dk = hashlib.pbkdf2_hmac('sha256', key, salt, 10_000, key_length + iv_length)

    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    ck = dk[:key_length]
    iv = dk[key_length:]
    cipher = Cipher(algorithms.AES256(ck), modes.CBC(iv))
    decryptor = cipher.decryptor()
    dec2 = decryptor.update(enc[block_size:]) + decryptor.finalize()

    last_byte = dec2[-1]
    if last_byte > block_size:
        raise Exception('bad padding')
    dec2 = dec2[:-last_byte]

    print(dec2)
    if dec2 == raw:
        breakpoint()
    breakpoint()

    ##

    dec = sec.decrypt(enc, key)
    assert dec == raw


@pytest.mark.parametrize('sec', [
    crypto.FernetCrypto(),
    crypto.AesgsmCrypto(),
    crypto.Chacha20Poly1305Crypto(),
])
def test_crypto_crypto(sec: crypto.Crypto) -> None:
    key = sec.generate_key()

    raw = b'hi there'
    enc = sec.encrypt(raw, key)

    dec = sec.decrypt(enc, key)
    assert dec == raw

    with pytest.raises(crypto.DecryptionError):
        sec.decrypt(enc, bytes([key[0] + 1 if key[0] < 255 else 0]) + key[1:])
