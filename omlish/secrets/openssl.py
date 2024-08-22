import hashlib
import secrets
import typing as ta

from .. import lang


if ta.TYPE_CHECKING:
    from cryptography.hazmat.primitives import ciphers as cry_ciphs
    from cryptography.hazmat.primitives.ciphers import algorithms as cry_algs
    from cryptography.hazmat.primitives.ciphers import modes as cry_modes

else:
    cry_ciphs = lang.proxy_import('cryptography.hazmat.primitives.ciphers')
    cry_algs = lang.proxy_import('cryptography.hazmat.primitives.ciphers.algorithms')
    cry_modes = lang.proxy_import('cryptography.hazmat.primitives.ciphers.modes')


class OpensslAes265CbcPbkdf2:
    """
    !!! https://docs.openssl.org/3.0/man7/passphrase-encoding/
    https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.Cipher
    https://stackoverflow.com/questions/16761458/how-to-decrypt-openssl-aes-encrypted-files-in-python
    https://github.com/openssl/openssl/blob/3c1713aeed4dc7d1ac25e9e365b8bd98afead638/apps/enc.c#L555-L573
    """

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
        elif len(salt) != self.salt_length:
            raise Exception('bad salt length')

        last_byte = self.block_size - (len(data) % self.block_size)
        raw = bytes([last_byte] * last_byte)

        cipher = self._make_cipher(key, salt)

        encryptor = cipher.encryptor()
        enc = encryptor.update(raw) + encryptor.finalize()

        return b''.join([
            self.prefix,
            salt,
            enc,
        ])

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
