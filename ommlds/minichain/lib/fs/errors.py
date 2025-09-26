import typing as ta

from omlish import lang

from ...tools.execution.errors import ToolExecutionError


##


class FsToolExecutionError(ToolExecutionError, lang.Abstract):
    pass


##


class RequestedPathError(FsToolExecutionError, lang.Abstract):
    def __init__(self, requested_path: str, *args: ta.Any) -> None:
        super().__init__(requested_path, *args)

        self.requested_path = requested_path


class RequestedPathMustBeAbsoluteError(RequestedPathError):
    @property
    def content(self) -> str:
        return f'Requested path {self.requested_path!r} must be absolute.'


class RequestedPathOutsideRootDirError(RequestedPathError):
    def __init__(
            self,
            requested_path: str,
            *,
            root_dir: str,
    ) -> None:
        super().__init__(
            requested_path,
            root_dir,
        )

        self.root_dir = root_dir

    @property
    def content(self) -> str:
        return f'Requested path {self.requested_path!r} was outside of permitted root directory {self.root_dir!r}.'


class RequestedPathWrongTypeError(RequestedPathError):
    def __init__(
            self,
            requested_path: str,
            *,
            expected_type: str,
            actual_type: str | None = None,
    ) -> None:
        super().__init__(
            requested_path,
            expected_type,
            actual_type,
        )

        self.expected_type = expected_type
        self.actual_type = actual_type

    @property
    def content(self) -> str:
        return ''.join([
            f'Requested path {self.requested_path!r} must be of type {self.expected_type!r}',
            *([f', but it is actually of type {self.actual_type!r}'] if self.actual_type is not None else []),
            '.',
        ])


class RequestedPathDoesNotExistError(RequestedPathError):
    def __init__(
            self,
            requested_path: str,
            *,
            suggested_paths: ta.Sequence[str] | None = None,
    ) -> None:
        super().__init__(
            requested_path,
            suggested_paths,
        )

        self.suggested_paths = suggested_paths

    @property
    def content(self) -> str:
        return ''.join([
            f'Requested path {self.requested_path!r} does not exist.',
            *([f' Did you mean one of these valid paths: {self.suggested_paths!r}?'] if self.suggested_paths else []),
        ])


class RequestedPathWriteNotPermittedError(RequestedPathError):
    @property
    def content(self) -> str:
        return f'Writes are not permitted to requested path {self.requested_path!r}.'
