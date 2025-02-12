# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import os
import struct
import sys
import typing as ta


@dc.dataclass(frozen=True)
class FcntlLockData:
    # cmd = {F_SETLK, F_SETLKW, F_GETLK}

    type: int  # {F_RDLCK, F_WRLCK, F_UNLCK}
    whence: int = os.SEEK_SET
    start: int = 0
    len: int = 0
    pid: int = 0

    #

    _STRUCT_PACKING_BY_PLATFORM: ta.ClassVar[ta.Mapping[str, ta.Sequence[ta.Tuple[str, str]]]] = {
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

    @classmethod
    def _struct_packing(cls) -> ta.Sequence[ta.Tuple[str, str]]:
        try:
            return cls._STRUCT_PACKING_BY_PLATFORM[sys.platform]
        except KeyError:
            raise OSError from None

    def pack(self) -> bytes:
        packing = self._struct_packing()
        fmt = ''.join(f for _, f in packing)
        tup = [getattr(self, a) for a, _ in packing]
        return struct.pack(fmt, *tup)

    @classmethod
    def unpack(cls, data: bytes) -> 'FcntlLockData':
        packing = cls._struct_packing()
        fmt = ''.join(f for _, f in packing)
        tup = struct.unpack(fmt, data)
        kw = {a: v for (a, _), v in zip(packing, tup)}
        return FcntlLockData(**kw)
