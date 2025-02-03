# ruff: noqa: UP006 UP007
# @omlish-lite
import gzip
import hashlib
import tarfile
import typing as ta

from omlish.lite.contextmanagers import ExitStacked

from .datarefs import OciDataRef
from .datarefs import OciDataRefInfo
from .datarefs import open_oci_data_ref


##


class WrittenOciDataTarGzFileInfo(ta.NamedTuple):
    tar_sz: int
    tar_sha256: str

    gz_sz: int
    gz_sha256: str


class OciDataTarGzWriter(ExitStacked):
    def __init__(self, f: ta.BinaryIO) -> None:
        super().__init__()

        self._f = f

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

    _gw: _FileWrapper
    _gf: gzip.GzipFile

    _tw: _FileWrapper
    _tf: tarfile.TarFile

    def info(self) -> WrittenOciDataTarGzFileInfo:
        return WrittenOciDataTarGzFileInfo(
            tar_sz=self._tw.size,
            tar_sha256=self._tw.sha256(),

            gz_sz=self._gw.size,
            gz_sha256=self._gw.sha256(),
        )

    def __enter__(self) -> 'OciDataTarGzWriter':
        super().__enter__()

        self._gw = self._FileWrapper(self._f)
        self._gf = self._enter_context(gzip.GzipFile(fileobj=self._gw, mode='wb'))  # type: ignore

        self._tw = self._FileWrapper(self._gf)
        self._tf = self._enter_context(tarfile.open(fileobj=self._tw, mode='w'))  # type: ignore

        return self

    def tar_file(self) -> tarfile.TarFile:
        return self._tf

    def add_file(self, ti: tarfile.TarInfo, f: ta.Optional[ta.BinaryIO] = None) -> None:
        self._tf.addfile(ti, f)


def write_oci_data_tar_gz_file(
        f: ta.BinaryIO,
        data: ta.Mapping[str, OciDataRef],
) -> WrittenOciDataTarGzFileInfo:
    with OciDataTarGzWriter(f) as tgw:
        for n, dr in data.items():
            ti = tarfile.TarInfo(name=n)
            ri = OciDataRefInfo(dr)
            ti.size = ri.size()
            with open_oci_data_ref(dr) as df:
                tgw.add_file(ti, df)

    return tgw.info()
