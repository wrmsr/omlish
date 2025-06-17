# @omlish-lite
# ruff: noqa: UP006 UP007 UP045
import dataclasses as dc


##


@dc.dataclass(frozen=True)
class SslCert:
    key_file: str
    cert_file: str
