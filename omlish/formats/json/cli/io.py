"""
TODO:
 - -I/-Ogz, lz4, etc
  - fnpairs? or not yet just do it
"""
import contextlib
import gzip
import typing as ta

from .... import lang


if ta.TYPE_CHECKING:
    import bz2 as _bz2
    import gzip as _gzip
    import lzma as _lzma
else:
    _bz2 = lang.proxy_import('bz2')
    _gzip = lang.proxy_import('gzip')
    _lzma = lang.proxy_import('lzma')


IoCodec: ta.TypeAlias = ta.Callable[[ta.IO, str], ta.ContextManager[ta.IO]]


# class TrampolineThread:
#     pass


@contextlib.contextmanager
def gzip_io_codec(f: ta.IO, mode: str) -> ta.ContextManager[ta.IO]:
    with gzip.open(f, mode) as o:
        yield o
