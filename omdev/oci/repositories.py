# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import os.path
import tarfile
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.os.paths import is_path_in_dir

from .datarefs import BytesOciDataRef
from .datarefs import FileOciDataRef
from .datarefs import OciDataRef
from .datarefs import TarFileOciDataRef


##


class OciRepository(Abstract):
    @abc.abstractmethod
    def contains_blob(self, digest: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def read_blob(self, digest: str) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def ref_blob(self, digest: str) -> OciDataRef:
        raise NotImplementedError

    @classmethod
    def of(
            cls,
            obj: ta.Union[
                'OciRepository',
                str,
                tarfile.TarFile,
                ta.Mapping[str, bytes],
            ],
    ) -> 'OciRepository':
        if isinstance(obj, OciRepository):
            return obj

        elif isinstance(obj, str):
            check.arg(os.path.isdir(obj))
            return DirectoryOciRepository(obj)

        elif isinstance(obj, tarfile.TarFile):
            return TarFileOciRepository(obj)

        elif isinstance(obj, ta.Mapping):
            return DictOciRepository(obj)

        else:
            raise TypeError(obj)


class FileOciRepository(OciRepository, Abstract):
    @abc.abstractmethod
    def read_file(self, path: str) -> bytes:
        raise NotImplementedError


#


class DirectoryOciRepository(FileOciRepository):
    def __init__(self, data_dir: str) -> None:
        super().__init__()

        self._data_dir = check.non_empty_str(data_dir)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._data_dir!r})'

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

    def contains_blob(self, digest: str) -> bool:
        return os.path.isfile(self.blob_full_path(digest))

    def read_blob(self, digest: str) -> bytes:
        return self.read_file(self.blob_path(digest))

    def ref_blob(self, digest: str) -> OciDataRef:
        return FileOciDataRef(self.blob_full_path(digest))


#


class TarFileOciRepository(FileOciRepository):
    def __init__(self, tar_file: tarfile.TarFile) -> None:
        super().__init__()

        check.arg('r' in tar_file.mode)

        self._tar_file = tar_file

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._tar_file!r})'

    def read_file(self, path: str) -> bytes:
        if (ti := self._tar_file.getmember(path)) is None:
            raise FileNotFoundError(path)
        with check.not_none(self._tar_file.extractfile(ti)) as f:
            return f.read()

    def blob_name(self, digest: str) -> str:
        scheme, value = digest.split(':')
        return os.path.join('blobs', scheme, value)

    def contains_blob(self, digest: str) -> bool:
        try:
            self._tar_file.getmember(self.blob_name(digest))
        except KeyError:
            return False
        else:
            return True

    def read_blob(self, digest: str) -> bytes:
        if (ti := self._tar_file.getmember(self.blob_name(digest))) is None:
            raise KeyError(digest)
        with check.not_none(self._tar_file.extractfile(ti)) as f:
            return f.read()

    def ref_blob(self, digest: str) -> OciDataRef:
        return TarFileOciDataRef(
            tar_file=self._tar_file,
            tar_info=self._tar_file.getmember(self.blob_name(digest)),
        )


#


class DictOciRepository(OciRepository):
    def __init__(self, blobs: ta.Mapping[str, bytes]) -> None:
        super().__init__()

        self._blobs = blobs

    def contains_blob(self, digest: str) -> bool:
        return digest in self._blobs

    def read_blob(self, digest: str) -> bytes:
        return self._blobs[digest]

    def ref_blob(self, digest: str) -> OciDataRef:
        return BytesOciDataRef(self._blobs[digest])
