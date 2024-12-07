# """
# TODO:
#  - -I/-Ogz, lz4, etc
#   - fnpairs? or not yet just do it
# """
# import abc
# import contextlib
# import dataclasses as dc
# import gzip
# import os
# import typing as ta
#
# from .... import lang
#
#
# if ta.TYPE_CHECKING:
#     import bz2 as _bz2
#     import gzip as _gzip
#     import lzma as _lzma
# else:
#     _bz2 = lang.proxy_import('bz2')
#     _gzip = lang.proxy_import('gzip')
#     _lzma = lang.proxy_import('lzma')
#
#
# ##
#
#
# class BaseIo(lang.Abstract):
#     def close(self) -> None:
#         raise NotImplementedError
#
#     def fileno(self) -> int | None:
#         return None
#
#
# class Input(BaseIo):
#     @abc.abstractmethod
#     def read(self, sz: int | None = None) -> bytes:
#         raise NotImplementedError
#
#
# class Output(BaseIo):
#     @abc.abstractmethod
#     def write(self, data: bytes) -> int:
#         raise NotImplementedError
#
#
# #
#
#
# DEFAULT_READ_SZ = 0x4000
#
#
# @dc.dataclass(frozen=True)
# class Fdio(Input, Output):
#     fd: int
#
#     default_read_sz: int = DEFAULT_READ_SZ
#
#     def read(self, sz: int | None = None) -> bytes:
#         return os.read(self.fd, sz or self.default_read_sz)
#
#     def write(self, data: bytes) -> int:
#         return os.write(self.fd, data)
#
#
# ##
#
#
# @contextlib.contextmanager
# def gzip_io_codec(f: ta.IO, mode: str) -> ta.ContextManager[ta.IO]:
#     with gzip.open(f, mode) as o:
#         yield o
