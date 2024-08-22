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
import contextlib
import fcntl
import os  # noqa
import subprocess  # noqa
import tempfile  # noqa
import typing as ta  # noqa

import pytest

from ... import check


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


class SubprocessFileInput(ta.NamedTuple):
    file_path: str
    pass_fds: ta.Sequence[int]


@contextlib.contextmanager
def _temp_subprocess_file_input(buf: bytes) -> ta.Iterator[SubprocessFileInput]:
    with tempfile.NamedTemporaryFile() as kf:
        kf.write(buf)
        kf.flush()
        yield SubprocessFileInput(kf.name, [])


@contextlib.contextmanager
def _pipe_fd_subprocess_file_input(buf: bytes) -> ta.Iterator[SubprocessFileInput]:
    rfd, wfd = os.pipe()
    closed_wfd = False
    try:
        if hasattr(fcntl, 'F_SETPIPE_SZ'):
            fcntl.fcntl(wfd, fcntl.F_SETPIPE_SZ, max(len(buf), 0x1000))
        os.write(wfd, buf)
        os.close(wfd)
        closed_wfd = True
        yield SubprocessFileInput(f'/dev/fd/{rfd}', [rfd])
    finally:
        if not closed_wfd:
            os.close(wfd)
        os.close(rfd)


class OpensslShellCrypto(Crypto):
    def __init__(
            self,
            *,
            cmd: ta.Sequence[str] = ('openssl',),
            timeout: float = 5.,
            file_input: ta.Callable[[bytes], ta.ContextManager[SubprocessFileInput]] = _temp_subprocess_file_input,
    ) -> None:
        super().__init__()
        self._cmd = cmd
        self._timeout = timeout
        self._file_input = file_input

    def generate_key(self, sz: int = 128) -> bytes:
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


@pytest.mark.parametrize('sec', [
    OpensslShellCrypto(),
    OpensslShellCrypto(file_input=_pipe_fd_subprocess_file_input),
])
def test_crypto(sec: OpensslShellCrypto) -> None:
    key = sec.generate_key()
    print(repr(key))

    raw = b'hi there'
    enc = sec.encrypt(raw, key)
    print(repr(enc))

    dec = sec.decrypt(enc, key)
    print(repr(dec))


def test_pipes():
    buf = b'hi'

    rfd, wfd = os.pipe()
    if hasattr(fcntl, 'F_SETPIPE_SZ'):
        fcntl.fcntl(wfd, fcntl.F_SETPIPE_SZ, max(len(buf), 0x1000))
    os.write(wfd, buf)
    os.close(wfd)

    ret = subprocess.run(
        ['cat', f'/dev/fd/{rfd}'],
        pass_fds=[rfd],
        stdout=subprocess.PIPE,
        check=True,
    )
    os.close(rfd)

    print(ret.stdout)
