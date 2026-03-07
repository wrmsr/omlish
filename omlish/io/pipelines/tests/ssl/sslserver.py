#!/usr/bin/env python3
# ruff: noqa: UP006 UP017 UP045
# @omlish-lite
"""
Zero-dependency HTTPS hello-world using stdlib only.

- Generates a temporary self-signed cert via `openssl` (must be installed).
- Serves HTTPS on https://127.0.0.1:8443/
- Responds to GET / with plaintext hello + some client info.

Try:
  python3 https_hello.py
  curl -k https://127.0.0.1:8443/
"""
import datetime
import http.server
import os
import shutil
import ssl
import subprocess
import tempfile
import typing as ta


##


LISTEN_HOST = '127.0.0.1'
LISTEN_PORT = 8443


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = 'PyHTTPSHello/0.1'

    def do_GET(self) -> None:
        # Only handle "/"
        if self.path != '/':
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'not found\n')
            return

        peer = getattr(self, 'client_address', None)
        peer_s = f'{peer[0]}:{peer[1]}' if peer else 'unknown'

        # SSL socket info (cipher, protocol, etc.) if available
        tls_info = ''
        try:
            sslsock = self.connection
            if isinstance(sslsock, ssl.SSLSocket):
                cipher = sslsock.cipher()
                version = sslsock.version()
                tls_info = (
                    f'tls_version: {version}\n'
                    f'cipher: {cipher}\n'
                )
        except Exception:  # noqa
            pass

        body = '\n'.join([
            f'hello world (over TLS)',
            '',
            f'time: {datetime.datetime.now(tz=datetime.timezone.utc).isoformat()}',
            f'peer: {peer_s}',
            f'method: {self.command}',
            f'path: {self.path}',
            f'http_version: {self.request_version}',
            '',
            tls_info,
        ]).encode('utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        # slightly nicer logs
        peer = f'{self.client_address[0]}:{self.client_address[1]}'
        msg = fmt % args
        print(f'[{peer}] {msg}')


def run_openssl(args: list) -> None:
    p = subprocess.run(  # noqa
        ['openssl', *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        text=True,
    )
    if p.returncode != 0:
        raise RuntimeError(
            "openssl failed:\n"
            f"  cmd: openssl {' '.join(args)}\n"
            f"  rc: {p.returncode}\n"
            f"  stdout:\n{p.stdout}\n"
            f"  stderr:\n{p.stderr}\n",
        )


def generate_self_signed_cert(tmpdir: str) -> ta.Tuple[str, str]:
    """
    Returns (cert_pem_path, key_pem_path).
    """
    if shutil.which('openssl') is None:
        raise RuntimeError('openssl not found on PATH')

    key_pem = os.path.join(tmpdir, 'key.pem')
    cert_pem = os.path.join(tmpdir, 'cert.pem')

    # Self-signed cert for CN=localhost (fine for local dev; curl -k ignores trust anyway)
    # openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=localhost"
    run_openssl(
        [
            'req',
            '-x509',
            '-newkey',
            'rsa:2048',
            '-nodes',
            '-keyout',
            key_pem,
            '-out',
            cert_pem,
            '-days',
            '365',
            '-subj',
            '/CN=localhost',
        ],
    )

    return cert_pem, key_pem


def main() -> None:
    with tempfile.TemporaryDirectory(prefix='py-https-hello-') as tmpdir:
        cert_pem, key_pem = generate_self_signed_cert(tmpdir)

        httpd = http.server.ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), Handler)

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # Optional: keep it simple and broad for local testing; stdlib defaults are OK too.
        # ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(certfile=cert_pem, keyfile=key_pem)

        # Wrap the server socket for TLS
        httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

        print(f'HTTPS hello-world listening on https://{LISTEN_HOST}:{LISTEN_PORT}/')
        print(f'  (self-signed cert generated in: {tmpdir})')
        print(f'Try:')
        print(f'  curl -k https://{LISTEN_HOST}:{LISTEN_PORT}/')
        print()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
