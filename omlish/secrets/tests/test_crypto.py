"""
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
import os  # noqa
import subprocess  # noqa
import tempfile  # noqa
import typing as ta  # noqa

from omlish import check


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


class OpensslShellCrypto(Crypto):
    _cmd: ta.Sequence[str] = ['openssl']
    _timeout: float = 5.

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
        with tempfile.NamedTemporaryFile() as kf:
            kf.write(key)
            kf.flush()
            ret = subprocess.run(
                [
                    *self._cmd,
                    'enc',
                    '-in', '-',
                    '-out', '-',
                    '-e',
                    '-aes256',
                    '-pbkdf2',
                    '-kfile', kf.name,
                ],
                input=data,
                stdout=subprocess.PIPE,
                timeout=self._timeout,
                check=True,
            )
            out = ret.stdout
            return out

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        with tempfile.NamedTemporaryFile() as kf:
            kf.write(key)
            kf.flush()
            ret = subprocess.run(
                [
                    *self._cmd,
                    'aes-256-cbc',
                    '-d',
                    '-pbkdf2',
                    '-in', '-',
                    '-out', '-',
                    '-kfile', kf.name,
                ],
                input=data,
                stdout=subprocess.PIPE,
                timeout=self._timeout,
                check=True,
            )
            out = ret.stdout
            return out


def test_crypto() -> None:
    sec = OpensslShellCrypto()

    key = sec.generate_key()
    print(repr(key))

    raw = b'hi there'
    enc = sec.encrypt(raw, key)
    print(repr(enc))

    dec = sec.decrypt(enc, key)
    print(repr(dec))

    # OpensslShellSecrets().generate_key()
    #
    # r0, w0 = os.pipe()
    # r1, w1 = os.pipe()

    # pipesize = -1
    # err_close_fds.extend((p2cread, p2cwrite))
    # if self.pipesize > 0 and hasattr(fcntl, "F_SETPIPE_SZ"):
    #     fcntl.fcntl(p2cwrite, fcntl.F_SETPIPE_SZ, self.pipesize)

    """
    @contextlib.contextmanager
    def _on_error_fd_closer(self):
        to_close = []
        try:
            yield to_close
        except:
            if hasattr(self, '_devnull'):
                to_close.append(self._devnull)
                del self._devnull
            for fd in to_close:
                try:
                    if _mswindows and isinstance(fd, Handle):
                        fd.Close()
                    else:
                        os.close(fd)
                except OSError:
                    pass
            raise

    def _stdin_write(self, input):
        if input:
            try:
                self.stdin.write(input)
            except BrokenPipeError:
                pass  # communicate() must ignore broken pipe errors.
            except OSError as exc:
                if exc.errno == errno.EINVAL:
                    # bpo-19612, bpo-30418: On Windows, stdin.write() fails
                    # with EINVAL if the child process exited or if the child
                    # process is still running but closed the pipe.
                    pass
                else:
                    raise

        try:
            self.stdin.close()
        except BrokenPipeError:
            pass  # communicate() must ignore broken pipe errors.
        except OSError as exc:
            if exc.errno == errno.EINVAL:
                pass
            else:
                raise
    """

    # subprocess.run(
    #     # ['cat', '/dev/fd/1'],
    #     ['ls', '-al', '/dev/fd'],
    #     input=b'barf',
    # )
    #
    # print()


def test_pipes():
    rfd, wfd = os.pipe()
    os.write(wfd, b'hi')
    os.close(wfd)
    ret = subprocess.run(
        ['cat', f'/dev/fd/{rfd}'],
        pass_fds=[rfd],
        stdout=subprocess.PIPE,
    )
    print(ret.stdout)
