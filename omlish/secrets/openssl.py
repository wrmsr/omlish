"""
TODO:
 - LibreSSL supports aes-256-gcm: https://crypto.stackexchange.com/a/76178
"""
import hashlib
import secrets
import subprocess
import typing as ta

from .. import lang
from .crypto import Crypto
from .crypto import DecryptionError
from .crypto import EncryptionError
from .subprocesses import SubprocessFileInputMethod
from .subprocesses import pipe_fd_subprocess_file_input  # noqa
from .subprocesses import temp_subprocess_file_input  # noqa


if ta.TYPE_CHECKING:
    from cryptography.hazmat.primitives import ciphers as cry_ciphs
    from cryptography.hazmat.primitives.ciphers import algorithms as cry_algs
    from cryptography.hazmat.primitives.ciphers import modes as cry_modes

else:
    cry_ciphs = lang.proxy_import('cryptography.hazmat.primitives.ciphers')
    cry_algs = lang.proxy_import('cryptography.hazmat.primitives.ciphers.algorithms')
    cry_modes = lang.proxy_import('cryptography.hazmat.primitives.ciphers.modes')


##


DEFAULT_KEY_SIZE = 64


def generate_key(sz: int = DEFAULT_KEY_SIZE) -> bytes:
    # !! https://docs.openssl.org/3.0/man7/passphrase-encoding/
    # Must not contain null bytes!
    return secrets.token_hex(sz).encode('ascii')


##


class OpensslAescbcCrypto(Crypto):
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

    def generate_key(self, sz: int = DEFAULT_KEY_SIZE) -> bytes:
        # This actually can handle null bytes, but we don't generate keys with them for compatibility.
        return generate_key(sz)

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
            raise EncryptionError('bad salt length')

        last_byte = self.block_size - (len(data) % self.block_size)
        raw = data + bytes([last_byte] * last_byte)

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
            raise DecryptionError('bad prefix')

        salt = data[len(self.prefix):self.block_size]
        cipher = self._make_cipher(key, salt)

        decryptor = cipher.decryptor()
        dec = decryptor.update(data[self.block_size:]) + decryptor.finalize()

        last_byte = dec[-1]
        if last_byte > self.block_size:
            raise DecryptionError('bad padding')

        return dec[:-last_byte]


##


class OpensslSubprocessAescbcCrypto(Crypto):
    def __init__(
            self,
            *,
            cmd: ta.Sequence[str] = ('openssl',),
            timeout: float = 5.,
            file_input: SubprocessFileInputMethod = temp_subprocess_file_input,
    ) -> None:
        super().__init__()

        self._cmd = cmd
        self._timeout = timeout
        self._file_input = file_input

    def generate_key(self, sz: int = DEFAULT_KEY_SIZE) -> bytes:
        return generate_key(sz)

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        # !! https://docs.openssl.org/3.0/man7/passphrase-encoding/
        # Must not contain null bytes!
        if 0 in key:
            raise Exception('invalid key')
        with self._file_input(key) as fi:
            proc = subprocess.Popen(
                [
                    *self._cmd,
                    'aes-256-cbc',

                    '-e',

                    '-pbkdf2',
                    '-salt',
                    '-iter', '10000',

                    '-in', '-',
                    '-out', '-',
                    '-kfile', fi.file_path,
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                pass_fds=[*fi.pass_fds],
            )
            out, err = proc.communicate(
                data,
                timeout=self._timeout,
            )
            if proc.returncode != 0:
                raise EncryptionError
            return out

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        # !! https://docs.openssl.org/3.0/man7/passphrase-encoding/
        # Must not contain null bytes!
        if 0 in key:
            raise Exception('invalid key')
        with self._file_input(key) as fi:
            proc = subprocess.Popen(
                [
                    *self._cmd,
                    'aes-256-cbc',

                    '-d',

                    '-pbkdf2',
                    '-salt',
                    '-iter', '10000',

                    '-in', '-',
                    '-out', '-',
                    '-kfile', fi.file_path,
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                pass_fds=[*fi.pass_fds],
            )
            out, err = proc.communicate(
                data,
                timeout=self._timeout,
            )
            if proc.returncode != 0:
                raise DecryptionError
            return out
