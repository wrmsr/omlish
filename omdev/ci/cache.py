# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import os.path
import shlex
import shutil
import typing as ta

from .shell import ShellCmd


##


@abc.abstractmethod
class FileCache(abc.ABC):
    @abc.abstractmethod
    def get_file(self, key: str) -> ta.Optional[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def put_file(self, key: str, file_path: str) -> ta.Optional[str]:
        raise NotImplementedError


#


class DirectoryFileCache(FileCache):
    def __init__(self, dir: str) -> None:  # noqa
        super().__init__()

        self._dir = dir

    #

    def get_cache_file_path(
            self,
            key: str,
            *,
            make_dirs: bool = False,
    ) -> str:
        if make_dirs:
            os.makedirs(self._dir, exist_ok=True)
        return os.path.join(self._dir, key)

    def format_incomplete_file(self, f: str) -> str:
        return os.path.join(os.path.dirname(f), f'_{os.path.basename(f)}.incomplete')

    #

    def get_file(self, key: str) -> ta.Optional[str]:
        cache_file_path = self.get_cache_file_path(key)
        if not os.path.exists(cache_file_path):
            return None
        return cache_file_path

    def put_file(self, key: str, file_path: str) -> None:
        cache_file_path = self.get_cache_file_path(key, make_dirs=True)
        shutil.copyfile(file_path, cache_file_path)


##


class ShellCache(abc.ABC):
    @abc.abstractmethod
    def get_file_cmd(self, key: str) -> ta.Optional[ShellCmd]:
        raise NotImplementedError

    class PutFileCmdContext(abc.ABC):
        def __init__(self) -> None:
            super().__init__()

            self._state: ta.Literal['open', 'committed', 'aborted'] = 'open'

        @property
        def state(self) -> ta.Literal['open', 'committed', 'aborted']:
            return self._state

        #

        @property
        @abc.abstractmethod
        def cmd(self) -> ShellCmd:
            raise NotImplementedError

        #

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_val is None:
                self.commit()
            else:
                self.abort()

        #

        @abc.abstractmethod
        def _commit(self) -> None:
            raise NotImplementedError

        def commit(self) -> None:
            if self._state == 'committed':
                return
            elif self._state == 'open':
                self._commit()
                self._state = 'committed'
            else:
                raise RuntimeError(self._state)

        #

        @abc.abstractmethod
        def _abort(self) -> None:
            raise NotImplementedError

        def abort(self) -> None:
            if self._state == 'aborted':
                return
            elif self._state == 'open':
                self._abort()
                self._state = 'committed'
            else:
                raise RuntimeError(self._state)

    @abc.abstractmethod
    def put_file_cmd(self, key: str) -> PutFileCmdContext:
        raise NotImplementedError


#


class DirectoryShellCache(ShellCache):
    def __init__(self, dfc: DirectoryFileCache) -> None:
        super().__init__()

        self._dfc = dfc

    def get_file_cmd(self, key: str) -> ta.Optional[ShellCmd]:
        f = self._dfc.get_file(key)
        if f is None:
            return None
        return ShellCmd(f'cat {shlex.quote(f)}')

    class _PutFileCmdContext(ShellCache.PutFileCmdContext):  # noqa
        def __init__(self, tf: str, f: str) -> None:
            super().__init__()

            self._tf = tf
            self._f = f

        @property
        def cmd(self) -> ShellCmd:
            return ShellCmd(f'cat > {shlex.quote(self._tf)}')

        def _commit(self) -> None:
            os.replace(self._tf, self._f)

        def _abort(self) -> None:
            os.unlink(self._tf)

    def put_file_cmd(self, key: str) -> ShellCache.PutFileCmdContext:
        f = self._dfc.get_cache_file_path(key, make_dirs=True)
        return self._PutFileCmdContext(self._dfc.format_incomplete_file(f), f)
