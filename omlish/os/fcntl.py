# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import os
import struct
import sys
import typing as ta


@dc.dataclass(frozen=True)
class FcntlLockData:
    type: int  # {F_RDLCK, F_WRLCK, F_UNLCK}
    whence: int = os.SEEK_SET
    start: int = 0
    len: int = 0
    pid: int = 0

    #

    _STRUCT_PACK_BY_PLATFORM: ta.ClassVar[ta.Mapping[str, ta.Sequence[ta.Tuple[str, str]]]] = {
        'linux': [
            ('type', 'h'),
            ('whence', 'h'),
            ('start', 'q'),
            ('len', 'q'),
            ('pid', 'i'),
        ],
        'darwin': [
            ('start', 'q'),
            ('len', 'q'),
            ('pid', 'i'),
            ('type', 'h'),
            ('whence', 'h'),
        ],
    }

    def pack(self) -> bytes:
        try:
            pack = self._STRUCT_PACK_BY_PLATFORM[sys.platform]
        except KeyError:
            raise OSError from None

        fmt = ''.join(f for _, f in pack)
        tup = [getattr(self, a) for a, _ in pack]
        return struct.pack(fmt, *tup)

    @classmethod
    def unpack(cls, data: bytes) -> 'FcntlLockData':
        try:
            pack = cls._STRUCT_PACK_BY_PLATFORM[sys.platform]
        except KeyError:
            raise OSError from None

        fmt = ''.join(f for _, f in pack)
        tup = struct.unpack(fmt, data)
        kw = {a: v for (a, _), v in zip(pack, tup)}
        return FcntlLockData(**kw)
