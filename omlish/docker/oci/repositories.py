# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import os.path
import typing as ta

from ...lite.check import check
from ...os.paths import is_path_in_dir
from .datarefs import BytesOciDataRef
from .datarefs import FileOciDataRef
from .datarefs import OciDataRef


##


class OciRepository(abc.ABC):
    @abc.abstractmethod
    def read_blob(self, digest: str) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def ref_blob(self, digest: str) -> OciDataRef:
        raise NotImplementedError


#


class DirectoryOciRepository(OciRepository):
    def __init__(self, data_dir: str) -> None:
        super().__init__()

        self._data_dir = check.non_empty_str(data_dir)

    def read_file(self, path: str) -> bytes:
        full_path = os.path.join(self._data_dir, path)
        check.arg(is_path_in_dir(self._data_dir, full_path))
        with open(full_path, 'rb') as f:
            return f.read()

    def blob_path(self, digest: str) -> str:
        scheme, value = digest.split(':')
        return os.path.join('blobs', scheme, value)

    def blob_full_path(self, digest: str) -> str:
        path = self.blob_path(digest)
        full_path = os.path.join(self._data_dir, path)
        check.arg(is_path_in_dir(self._data_dir, full_path))
        return full_path

    def read_blob(self, digest: str) -> bytes:
        return self.read_file(self.blob_path(digest))

    def ref_blob(self, digest: str) -> OciDataRef:
        return FileOciDataRef(self.blob_full_path(digest))


#


class DictionaryOciRepository(OciRepository):
    def __init__(self, blobs: ta.Mapping[str, bytes]) -> None:
        super().__init__()

        self._blobs = blobs

    def read_blob(self, digest: str) -> bytes:
        return self._blobs[digest]

    def ref_blob(self, digest: str) -> OciDataRef:
        return BytesOciDataRef(self._blobs[digest])
