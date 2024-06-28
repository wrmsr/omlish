import dataclasses as dc
import ssl
import typing as ta

from .config import SECONDS


@dc.dataclass(frozen=True, kw_only=True)
class SslConfig:
    ca_certs: str | None = None

    certfile: str | None = None
    keyfile: str | None = None
    keyfile_password: str | None = None

    ciphers: str = 'ECDHE+AESGCM'

    alpn_protocols: ta.Sequence[str] = ('h2', 'http/1.1')

    verify_flags: ssl.VerifyFlags | None = None
    verify_mode: ssl.VerifyMode | None = None

    ssl_handshake_timeout: int | float = 60 * SECONDS


def create_ssl_context(ssl_cfg: SslConfig) -> ssl.SSLContext | None:
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.set_ciphers(ssl_cfg.ciphers)
    context.minimum_version = ssl.TLSVersion.TLSv1_2  # RFC 7540 Section 9.2: MUST be TLS >=1.2
    context.options = ssl.OP_NO_COMPRESSION  # RFC 7540 Section 9.2.1: MUST disable compression
    context.set_alpn_protocols(ssl_cfg.alpn_protocols)

    if ssl_cfg.certfile is not None and ssl_cfg.keyfile is not None:
        context.load_cert_chain(
            certfile=ssl_cfg.certfile,
            keyfile=ssl_cfg.keyfile,
            password=ssl_cfg.keyfile_password,
        )

    if ssl_cfg.ca_certs is not None:
        context.load_verify_locations(ssl_cfg.ca_certs)
    if ssl_cfg.verify_mode is not None:
        context.verify_mode = ssl_cfg.verify_mode
    if ssl_cfg.verify_flags is not None:
        context.verify_flags = ssl_cfg.verify_flags

    return context
