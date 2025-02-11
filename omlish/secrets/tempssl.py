# @omlish-lite
# ruff: noqa: UP006 UP007
import dataclasses as dc
import os.path
import tempfile
import typing as ta

from ..lite.cached import cached_nullary
from ..subprocesses.run import SubprocessRun
from ..subprocesses.run import SubprocessRunnable
from ..subprocesses.run import SubprocessRunOutput
from .ssl import SslCert


class TempSslCert(ta.NamedTuple):
    cert: SslCert
    temp_dir: str


@dc.dataclass(frozen=True)
class TempSslCertGenerator(SubprocessRunnable[TempSslCert]):
    @cached_nullary
    def temp_dir(self) -> str:
        return tempfile.mkdtemp()

    @cached_nullary
    def make_run(self) -> SubprocessRun:
        return SubprocessRun.of(
            'openssl',
            'req',
            '-x509',
            '-newkey', 'rsa:2048',

            '-keyout', 'key.pem',
            '-out', 'cert.pem',

            '-days', '365',

            '-nodes',

            '-subj', '/CN=localhost',
            '-addext', 'subjectAltName = DNS:localhost,IP:127.0.0.1',

            cwd=self.temp_dir(),
            capture_output=True,
            check=False,
        )

    def handle_run_output(self, proc: SubprocessRunOutput) -> TempSslCert:
        if proc.returncode:
            raise RuntimeError(f'Failed to generate temp ssl cert: {proc.stderr=}')

        key_file = os.path.join(self.temp_dir(), 'key.pem')
        cert_file = os.path.join(self.temp_dir(), 'cert.pem')
        for file in [key_file, cert_file]:
            if not os.path.isfile(file):
                raise RuntimeError(f'Failed to generate temp ssl cert (file not found): {file}')

        return TempSslCert(
            SslCert(
                key_file=key_file,
                cert_file=cert_file,
            ),
            temp_dir=self.temp_dir(),
        )


def generate_temp_localhost_ssl_cert() -> TempSslCert:
    return TempSslCertGenerator().run()
