import os.path
import stat

from omlish import check

from ...tools.execution.context import tool_context
from ...tools.execution.permissions import tool_permission_decider
from ...tools.permissions.fs import FsToolPermissionTarget
from .binfiles import has_binary_file_extension
from .binfiles import is_binary_file
from .errors import RequestedPathDoesNotExistError
from .errors import RequestedPathOutsideRootDirError
from .errors import RequestedPathWriteNotPermittedError
from .errors import RequestedPathWrongTypeError
from .suggestions import get_path_suggestions


##


class FsContext:
    def __init__(
            self,
            *,
            root_dir: str | None = None,
    ) -> None:
        super().__init__()

        self._root_dir = root_dir

        self._abs_root_dir = os.path.abspath(root_dir) if root_dir is not None else None

    #

    async def check_requested_path(self, req_path: str) -> None:
        await tool_permission_decider().check_allowed(FsToolPermissionTarget(req_path, 'r'))

        abs_req_path = os.path.abspath(req_path)

        if (
            self._abs_root_dir is None or
            not (
                abs_req_path == self._abs_root_dir or
                abs_req_path.startswith(self._abs_root_dir + os.path.sep)
            )
        ):
            raise RequestedPathOutsideRootDirError(
                req_path,
                root_dir=check.not_none(self._root_dir),
            )

    #

    async def check_stat_dir(self, req_path: str) -> os.stat_result:
        await self.check_requested_path(req_path)

        try:
            st = os.stat(req_path)
        except FileNotFoundError:
            raise RequestedPathDoesNotExistError(
                req_path,
                suggested_paths=get_path_suggestions(
                    req_path,
                    filter=lambda e: e.is_dir(),
                ),
            ) from None

        if not stat.S_ISDIR(st.st_mode):
            raise RequestedPathWrongTypeError(
                req_path,
                expected_type='dir',
                **(dict(actual_type='file') if stat.S_ISREG(st.st_mode) else {}),
            )

        return st

    async def check_stat_file(
            self,
            req_path: str,
            *,
            text: bool = False,
            write: bool = False,
    ) -> os.stat_result:
        await self.check_requested_path(req_path)

        try:
            st = os.stat(req_path)
        except FileNotFoundError:
            raise RequestedPathDoesNotExistError(
                req_path,
                suggested_paths=get_path_suggestions(
                    req_path,
                    filter=lambda e: (e.is_file() and not (text and has_binary_file_extension(e.name))),
                ),
            ) from None

        if not stat.S_ISREG(st.st_mode):
            is_dir = stat.S_ISDIR(st.st_mode)
            raise RequestedPathWrongTypeError(
                req_path,
                expected_type='file',
                **(dict(actual_type='dir') if is_dir else {}),
            )

        if text and is_binary_file(req_path, st=st):
            raise RequestedPathWrongTypeError(
                req_path,
                expected_type='text file',
                actual_type='binary file',
            )

        if write:
            await self.check_writes_permitted(req_path)

        return st

    #

    async def check_writes_permitted(self, req_path: str) -> str:
        if not await tool_permission_decider().is_allowed(FsToolPermissionTarget(req_path, 'w')):
            raise RequestedPathWriteNotPermittedError(req_path)

        return req_path


def tool_fs_context() -> FsContext:
    return tool_context()[FsContext]
