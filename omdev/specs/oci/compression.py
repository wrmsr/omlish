# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import enum


##


class OciCompression(enum.Enum):
    GZIP = enum.auto()
    ZSTD = enum.auto()
