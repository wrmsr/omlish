"""
TODO:
 - must read file before editing
 - must re-read file if file has been modified
 - loosened replacer helpers
 - accept diff format impl
 - injectable confirmation, diff format
"""
from omlish import lang

from ....tools.execution.catalog import ToolCatalogEntry
from ....tools.execution.reflect import reflect_tool_catalog_entry
from ..context import tool_fs_context
from ..errors import RequestedPathError


##


class EditToolError(RequestedPathError, lang.Abstract):
    pass


class EmptyNewStringError(EditToolError):
    @property
    def content(self) -> str:
        return f'The requested edit to {self.requested_path!r} was given an empty "old_string" parameter.'


class OldStringNotPresentError(EditToolError):
    @property
    def content(self) -> str:
        return f'The requested edit to {self.requested_path!r} did not contain the given "old_string" parameter.'


class OldStringPresentMultipleTimesError(EditToolError):
    @property
    def content(self) -> str:
        return f'The requested edit to {self.requested_path!r} contained the given "old_string" parameter multiple times.'  # noqa


##


def execute_edit_tool(
        *,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
) -> str:
    """
    Edits the given file by replacing the string given by the 'old_string' parameter with the string given by the
    'new_string' parameter.

    The file must exist, must be a valid text file, and must be given as an absolute path.

    If the 'replace_all' parameter is false (the default) then 'new_string' must be present exactly once in the file,
    otherwise the operation will fail. If 'replace_all' is true then all instances of 'old_string' will be replaced by
    'new_string', but the operation will fail if there are no instances of 'old_string'
    present in the file.

    For the operation to succeed, both 'old_string' and 'new_string' must be EXACT, including all exact indentation and
    other whitespace. This *includes* trailing newlines - this operates on the file as a single string, not a list of
    lines.

    Args:
        file_path: The path of the file to edit. Must be an absolute path.
        old_string: The old string to be replaced. May not be empty, and must be exact, including all exact whitespace.
        new_string: The new string to replace the old string with.
        replace_all: If false (the default) then exactly one instance of 'old_string' must be present in the file to be
            replaced. If true then all instances of 'old_string' will be replaced by 'new_string', but at least one
            instance of 'old_string' must be present in the file.
    """

    if not old_string:
        raise EmptyNewStringError(file_path)

    ctx = tool_fs_context()
    ctx.check_stat_file(file_path, text=True, write=True)

    with open(file_path) as f:
        old_file = f.read()

    n = old_file.count(old_string)
    if not n:
        raise OldStringNotPresentError(file_path)

    if not replace_all and n != 1:
        raise OldStringPresentMultipleTimesError(file_path)

    new_file = old_file.replace(old_string, new_string)

    # FIXME: confirm lol

    with open(file_path, 'w') as f:
        f.write(new_file)

    return 'The file has been edited successfully.'


@lang.cached_function
def edit_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(execute_edit_tool)
