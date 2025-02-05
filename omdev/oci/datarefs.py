# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import dataclasses as dc
import functools
import hashlib
import io
import os.path
import shutil
import tarfile
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check


##


@dc.dataclass(frozen=True)
class OciDataRef(abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True)
class BytesOciDataRef(OciDataRef):
    data: bytes


@dc.dataclass(frozen=True)
class FileOciDataRef(OciDataRef):
    path: str


@dc.dataclass(frozen=True)
class TarFileOciDataRef(OciDataRef):
    tar_file: tarfile.TarFile
    tar_info: tarfile.TarInfo


##


@functools.singledispatch
def write_oci_data_ref_to_file(
        src_data: OciDataRef,
        dst_file: str,
        *,
        symlink: bool = False,  # noqa
        chunk_size: int = 1024 * 1024,
) -> None:
    with open_oci_data_ref(src_data) as f_src:
        with open(dst_file, 'wb') as f_dst:
            shutil.copyfileobj(f_src, f_dst, length=chunk_size)  # noqa


@write_oci_data_ref_to_file.register
def _(
        src_data: FileOciDataRef,
        dst_file: str,
        *,
        symlink: bool = False,
        **kwargs: ta.Any,
) -> None:
    if symlink:
        os.symlink(
            os.path.relpath(src_data.path, os.path.dirname(dst_file)),
            dst_file,
        )
    else:
        shutil.copyfile(src_data.path, dst_file)


#


@functools.singledispatch
def open_oci_data_ref(data: OciDataRef) -> ta.BinaryIO:
    raise TypeError(data)


@open_oci_data_ref.register
def _(data: FileOciDataRef) -> ta.BinaryIO:
    return open(data.path, 'rb')


@open_oci_data_ref.register
def _(data: BytesOciDataRef) -> ta.BinaryIO:
    return io.BytesIO(data.data)


@open_oci_data_ref.register
def _(data: TarFileOciDataRef) -> ta.BinaryIO:
    return check.not_none(data.tar_file.extractfile(data.tar_info))  # type: ignore[return-value]


#


@functools.singledispatch
def get_oci_data_ref_size(data: OciDataRef) -> int:
    raise TypeError(data)


@get_oci_data_ref_size.register
def _(data: FileOciDataRef) -> int:
    return os.path.getsize(data.path)


@get_oci_data_ref_size.register
def _(data: BytesOciDataRef) -> int:
    return len(data.data)


@get_oci_data_ref_size.register
def _(data: TarFileOciDataRef) -> int:
    return data.tar_info.size


##


@dc.dataclass(frozen=True)
class OciDataRefInfo:
    data: OciDataRef

    @cached_nullary
    def sha256(self) -> str:
        with open_oci_data_ref(self.data) as f:
            return hashlib.file_digest(f, 'sha256').hexdigest()  # type: ignore[arg-type]

    @cached_nullary
    def digest(self) -> str:
        return f'sha256:{self.sha256()}'

    @cached_nullary
    def size(self) -> int:
        return get_oci_data_ref_size(self.data)
