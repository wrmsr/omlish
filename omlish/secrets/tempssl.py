# @omlish-lite
# ruff: noqa: UP006 UP007
import os.path
import subprocess
import tempfile
import typing as ta

from .ssl import SslCert


class TempSslCert(ta.NamedTuple):
    cert: SslCert
    temp_dir: str


def generate_temp_localhost_ssl_cert() -> TempSslCert:
    temp_dir = tempfile.mkdtemp()

    proc = subprocess.run(
        [
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
        ],
        cwd=temp_dir,
        capture_output=True,
        check=False,
    )

    if proc.returncode:
        raise RuntimeError(f'Failed to generate temp ssl cert: {proc.stderr=}')

    return TempSslCert(
        SslCert(
            key_file=os.path.join(temp_dir, 'key.pem'),
            cert_file=os.path.join(temp_dir, 'cert.pem'),
        ),
        temp_dir,
    )
