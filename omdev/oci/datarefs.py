# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import dataclasses as dc
import hashlib
import io
import os.path
import shutil
import typing as ta

from omlish.lite.cached import cached_nullary


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


##


@dc.dataclass(frozen=True)
class OciDataRefInfo:
    data: OciDataRef

    @cached_nullary
    def sha256(self) -> str:
        if isinstance(self.data, FileOciDataRef):
            with open(self.data.path, 'rb') as f:
                return hashlib.file_digest(f, 'sha256').hexdigest()  # noqa

        elif isinstance(self.data, BytesOciDataRef):
            return hashlib.sha256(self.data.data).hexdigest()

        else:
            raise TypeError(self.data)

    @cached_nullary
    def digest(self) -> str:
        return f'sha256:{self.sha256()}'

    @cached_nullary
    def size(self) -> int:
        if isinstance(self.data, FileOciDataRef):
            return os.path.getsize(self.data.path)

        elif isinstance(self.data, BytesOciDataRef):
            return len(self.data.data)

        else:
            raise TypeError(self.data)


def write_oci_data_ref_to_file(
        data: OciDataRef,
        dst: str,
        *,
        symlink: bool = False,
) -> None:
    if isinstance(data, FileOciDataRef):
        if symlink:
            os.symlink(
                os.path.relpath(data.path, os.path.dirname(dst)),
                dst,
            )
        else:
            shutil.copyfile(data.path, dst)

    elif isinstance(data, BytesOciDataRef):
        with open(dst, 'wb') as f:
            f.write(data.data)

    else:
        raise TypeError(data)


def open_oci_data_ref(data: OciDataRef) -> ta.BinaryIO:
    if isinstance(data, FileOciDataRef):
        return open(data.path, 'rb')

    elif isinstance(data, BytesOciDataRef):
        return io.BytesIO(data.data)

    else:
        raise TypeError(data)
