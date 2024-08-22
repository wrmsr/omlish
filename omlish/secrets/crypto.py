"""
TODO:
 - cryptography vs pycryptodome[x]
 - standardize failure exception
 - chains - take first
 - keysets

See:
 - https://soatok.blog/2020/05/13/why-aes-gcm-sucks/
 - https://pycryptodome.readthedocs.io/en/latest/src/cipher/chacha20_poly1305.html

==

https://www.tecmint.com/gpg-encrypt-decrypt-files/

==

gpg --batch --passphrase '' --quick-gen-key wrmsr default default
gpg --batch --passphrase '' --quick-gen-key wrmsr2 default default
echo 'hi there' > secret.txt
gpg -e -u wrmsr -r wrmsr2 secret.txt
gpg -d -o secret2.txt secret.txt.gpg

gpg --batch -c --passphrase-file /var/secret.key -o some.gpg toencrypt.txt

openssl rand -rand /dev/urandom 128 > barf.key
openssl enc -in secret.txt -out secret.txt.enc -e -aes256 -pbkdf2 -kfile barf.key
openssl aes-256-cbc -d -pbkdf2 -in secret.txt.enc -out secret3.txt -kfile barf.key

https://wiki.openssl.org/index.php/Enc#Options
-pass 'file:...'

==

https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.Cipher

import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
key = os.urandom(32)
iv = os.urandom(16)
cipher = Cipher(algorithms.AES256(key), modes.CBC(iv))
encryptor = cipher.encryptor()
ct = encryptor.update(b"a secret message") + encryptor.finalize()
decryptor = cipher.decryptor()
decryptor.update(ct) + decryptor.finalize()

"""
import abc
import secrets
import subprocess
import typing as ta

from .. import lang
from .subprocesses import SubprocessFileInputMethod
from .subprocesses import pipe_fd_subprocess_file_input  # noqa
from .subprocesses import temp_subprocess_file_input  # noqa


if ta.TYPE_CHECKING:
    from cryptography import exceptions as cry_exc
    from cryptography import fernet as cry_fernet
    from cryptography.hazmat.primitives.ciphers import aead as cry_aead
else:
    cry_aead = lang.proxy_import('cryptography.hazmat.primitives.ciphers.aead')
    cry_exc = lang.proxy_import('cryptography.exceptions')
    cry_fernet = lang.proxy_import('cryptography.fernet')


##


class EncryptionError(Exception):
    pass


class DecryptionError(Exception):
    pass


class Crypto(abc.ABC):
    @abc.abstractmethod
    def generate_key(self) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def decrypt(self, data: bytes, key: bytes) -> bytes:
        raise NotImplementedError


##


class OpensslSubprocessCrypto(Crypto):
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

    DEFAULT_KEY_SIZE: ta.ClassVar[int] = 1024

    def generate_key(self, sz: int = DEFAULT_KEY_SIZE) -> bytes:
        return secrets.token_bytes(sz)

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        with self._file_input(key.hex().upper().encode('ascii')) as fi:
            proc = subprocess.Popen(
                [
                    *self._cmd,
                    'aes-256-cbc',
                    '-e',
                    '-pbkdf2',

                    '-in', '-',
                    '-out', '-',
                    '-pass', f'file:{fi.file_path}',
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
        with self._file_input(key.hex().upper().encode('ascii')) as fi:
            proc = subprocess.Popen(
                [
                    *self._cmd,
                    'aes-256-cbc',
                    '-d',
                    '-pbkdf2',

                    '-in', '-',
                    '-out', '-',
                    '-pass', f'file:{fi.file_path}',
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


##


class FernetCrypto(Crypto):

    def generate_key(self) -> bytes:
        return cry_fernet.Fernet.generate_key()

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        try:
            f = cry_fernet.Fernet(key)
        except ValueError as e:
            raise EncryptionError from e
        return f.encrypt(data)

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        try:
            f = cry_fernet.Fernet(key)
        except ValueError as e:
            raise DecryptionError from e
        try:
            return f.decrypt(data)
        except cry_fernet.InvalidToken as e:
            raise DecryptionError from e


class AesgsmCrypto(Crypto):
    """https://stackoverflow.com/a/59835994"""

    def generate_key(self) -> bytes:
        return secrets.token_bytes(32)

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        nonce = secrets.token_bytes(12)
        return nonce + cry_aead.AESGCM(key).encrypt(nonce, data, b'')

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        try:
            return cry_aead.AESGCM(key).decrypt(data[:12], data[12:], b'')
        except cry_exc.InvalidTag as e:
            raise DecryptionError from e


class Chacha20Poly1305Crypto(Crypto):
    """https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.ChaCha20Poly1305"""  # noqa

    def generate_key(self) -> bytes:
        return cry_aead.ChaCha20Poly1305.generate_key()

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        nonce = secrets.token_bytes(12)
        return nonce + cry_aead.ChaCha20Poly1305(key).encrypt(nonce, data, b'')

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        try:
            return cry_aead.ChaCha20Poly1305(key).decrypt(data[:12], data[12:], b'')
        except cry_exc.InvalidTag as e:
            raise DecryptionError from e
