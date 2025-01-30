# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import dataclasses as dc
import hashlib
import os.path
import shutil
import typing as ta


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


class OciDataRefInfo(ta.NamedTuple):
    data: OciDataRef
    sha256: str
    size: int

    @property
    def digest(self) -> str:
        return f'sha256:{self.sha256}'


def get_oci_data_ref_info(data: OciDataRef) -> OciDataRefInfo:
    if isinstance(data, FileOciDataRef):
        with open(data.path, 'rb') as f:
            hx = hashlib.file_digest(f, 'sha256').hexdigest()  # noqa
        sz = os.path.getsize(data.path)
        return OciDataRefInfo(
            data=data,
            sha256=hx,
            size=sz,
        )

    elif isinstance(data, BytesOciDataRef):
        return OciDataRefInfo(
            data=data,
            sha256=hashlib.sha256(data.data).hexdigest(),
            size=len(data.data),
        )

    else:
        raise TypeError(data)


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
