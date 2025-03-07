# ruff: noqa: UP006 UP007
# @omlish-lite
import gzip
import hashlib
import tarfile
import typing as ta

from omlish.lite.contextmanagers import ExitStacked

from .compression import OciCompression
from .datarefs import OciDataRef
from .datarefs import OciDataRefInfo
from .datarefs import open_oci_data_ref


##


class WrittenOciDataTarFileInfo(ta.NamedTuple):
    compressed_sz: int
    compressed_sha256: str

    tar_sz: int
    tar_sha256: str


class OciDataTarWriter(ExitStacked):
    def __init__(
            self,
            f: ta.BinaryIO,
            compression: ta.Optional[OciCompression] = None,
            *,
            gzip_level: int = 1,
            zstd_level: int = 10,
    ) -> None:
        super().__init__()

        self._f = f
        self._compression = compression

        self._gzip_level = gzip_level
        self._zstd_level = zstd_level

    class _FileWrapper:
        def __init__(self, f):
            super().__init__()

            self._f = f
            self._c = 0
            self._h = hashlib.sha256()

        @property
        def size(self) -> int:
            return self._c

        def sha256(self) -> str:
            return self._h.hexdigest()

        def write(self, d):
            self._c += len(d)
            self._h.update(d)
            self._f.write(d)

        def tell(self) -> int:
            return self._f.tell()

    _cw: _FileWrapper
    _cf: ta.BinaryIO

    _tw: _FileWrapper
    _tf: tarfile.TarFile

    def info(self) -> WrittenOciDataTarFileInfo:
        return WrittenOciDataTarFileInfo(
            compressed_sz=self._cw.size,
            compressed_sha256=self._cw.sha256(),

            tar_sz=self._tw.size,
            tar_sha256=self._tw.sha256(),
        )

    def _enter_contexts(self) -> None:
        self._cw = self._FileWrapper(self._f)

        if self._compression is OciCompression.GZIP:
            self._cf = self._enter_context(
                gzip.GzipFile(  # type: ignore
                    fileobj=self._cw,
                    mode='wb',
                    compresslevel=self._gzip_level,
                ),
            )

        elif self._compression is OciCompression.ZSTD:
            zc = __import__('zstandard').ZstdCompressor(
                level=self._zstd_level,
            )
            self._cf = self._enter_context(zc.stream_writer(self._cw))

        elif self._compression is None:
            self._cf = self._cw  # type: ignore

        else:
            raise ValueError(self._compression)

        #

        self._tw = self._FileWrapper(self._cf)

        self._tf = self._enter_context(
            tarfile.open(  # type: ignore  # noqa
                fileobj=self._tw,
                mode='w',
            ),
        )

    def tar_file(self) -> tarfile.TarFile:
        return self._tf

    def add_file(self, ti: tarfile.TarInfo, f: ta.Optional[ta.BinaryIO] = None) -> None:
        self._tf.addfile(ti, f)


def write_oci_data_tar_file(
        f: ta.BinaryIO,
        data: ta.Mapping[str, OciDataRef],
) -> WrittenOciDataTarFileInfo:
    with OciDataTarWriter(f) as tgw:
        for n, dr in data.items():
            ti = tarfile.TarInfo(name=n)
            ri = OciDataRefInfo(dr)
            ti.size = ri.size()
            with open_oci_data_ref(dr) as df:
                tgw.add_file(ti, df)

    return tgw.info()
