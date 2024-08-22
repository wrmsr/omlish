"""
TODO:
 - stdlib secrets, secure rand gen

FIXME:
 - macos pipe size lol, and just like checking at all

https://www.tecmint.com/gpg-encrypt-decrypt-files/

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
"""
import abc
import subprocess
import typing as ta

from .. import check
from .. import lang
from .subprocesses import SubprocessFileInputMethod
from .subprocesses import pipe_fd_subprocess_file_input  # noqa
from .subprocesses import temp_subprocess_file_input  # noqa


if ta.TYPE_CHECKING:
    from cryptography import fernet
else:
    fernet = lang.proxy_import('cryptography.fernet')


##


class Crypto(abc.ABC):
    DEFAULT_KEY_SIZE: ta.ClassVar[int] = 1024

    @abc.abstractmethod
    def generate_key(self, sz: int = DEFAULT_KEY_SIZE) -> bytes:
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

    def generate_key(self, sz: int = Crypto.DEFAULT_KEY_SIZE) -> bytes:
        check.arg(sz > 0)
        ret = subprocess.run(
            [
                *self._cmd,
                'rand',
                '-rand',
                '/dev/urandom',
                str(sz),
            ],
            stdout=subprocess.PIPE,
            timeout=self._timeout,
            check=True,
        )
        out = ret.stdout
        check.equal(len(out), sz)
        return out

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        with self._file_input(key) as fi:
            ret = subprocess.run(
                [
                    *self._cmd,
                    'enc',
                    '-in', '-',
                    '-out', '-',
                    '-e',
                    '-aes256',
                    '-pbkdf2',
                    '-kfile', fi.file_path,
                ],
                input=data,
                stdout=subprocess.PIPE,
                timeout=self._timeout,
                check=True,
                pass_fds=[*fi.pass_fds],
            )
            out = ret.stdout
            return out

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        with self._file_input(key) as fi:
            ret = subprocess.run(
                [
                    *self._cmd,
                    'aes-256-cbc',
                    '-d',
                    '-pbkdf2',
                    '-in', '-',
                    '-out', '-',
                    '-kfile', fi.file_path,
                ],
                input=data,
                stdout=subprocess.PIPE,
                timeout=self._timeout,
                check=True,
                pass_fds=[*fi.pass_fds],
            )
            out = ret.stdout
            return out


##


class FernetCrypto(Crypto):

    def generate_key(self, sz: int = Crypto.DEFAULT_KEY_SIZE) -> bytes:
        return fernet.Fernet.generate_key()

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        return fernet.Fernet(key).encrypt(data)

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        return fernet.Fernet(key).decrypt(data)
