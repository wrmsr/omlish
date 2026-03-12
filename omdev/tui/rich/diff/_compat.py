# @omlish-llm-author "gpt-5.4-thinking"
import dataclasses as dc
import typing as ta

from ....diffs.types import ExtendedHeaderKind
from ....diffs.types import FilePatch
from ....diffs.types import Hunk
from ....diffs.types import HunkLine
from ....diffs.types import HunkLineKind
from ....diffs.types import PatchSet


##


@dc.dataclass(frozen=True, slots=True)
class _CompatLine:
    value: str
    is_removed: bool
    is_added: bool
    is_context: bool
    source_line_no: int | None
    target_line_no: int | None


class _CompatHunk:
    def __init__(self, hunk: Hunk) -> None:
        self._hunk = hunk

    @property
    def source_start(self) -> int:
        return self._hunk.old_start

    @property
    def source_length(self) -> int:
        return self._hunk.old_count

    @property
    def target_start(self) -> int:
        return self._hunk.new_start

    @property
    def target_length(self) -> int:
        return self._hunk.new_count

    @property
    def section_header(self) -> str | None:
        return self._hunk.section

    def __iter__(self) -> ta.Iterator[_CompatLine]:
        old_lineno = self._hunk.old_start
        new_lineno = self._hunk.new_start

        for hl in self._hunk.lines:
            if hl.kind == HunkLineKind.CONTEXT:
                yield _CompatLine(
                    value=_render_hunk_line_value(hl),
                    is_removed=False,
                    is_added=False,
                    is_context=True,
                    source_line_no=old_lineno,
                    target_line_no=new_lineno,
                )
                old_lineno += 1
                new_lineno += 1

            elif hl.kind == HunkLineKind.REMOVE:
                yield _CompatLine(
                    value=_render_hunk_line_value(hl),
                    is_removed=True,
                    is_added=False,
                    is_context=False,
                    source_line_no=old_lineno,
                    target_line_no=None,
                )
                old_lineno += 1

            elif hl.kind == HunkLineKind.ADD:
                yield _CompatLine(
                    value=_render_hunk_line_value(hl),
                    is_removed=False,
                    is_added=True,
                    is_context=False,
                    source_line_no=None,
                    target_line_no=new_lineno,
                )
                new_lineno += 1

            else:
                raise AssertionError(hl.kind)

    def source_lines(self) -> list[_CompatLine]:
        return [ln for ln in self if ln.is_removed or ln.is_context]

    def target_lines(self) -> list[_CompatLine]:
        return [ln for ln in self if ln.is_added or ln.is_context]


class _CompatPatchedFile:
    def __init__(self, fp: FilePatch) -> None:
        self._fp = fp

    def __iter__(self) -> ta.Iterator[_CompatHunk]:
        for hunk in self._fp.hunks:
            yield _CompatHunk(hunk)

    @property
    def path(self) -> str:
        return self._fp.new_path or self._fp.old_path or '<unknown>'

    @property
    def source_file(self) -> str:
        return self._fp.old_path or self.path

    @property
    def added(self) -> int:
        return self._fp.added_count

    @property
    def removed(self) -> int:
        return self._fp.removed_count

    @property
    def is_added_file(self) -> bool:
        return self._fp.is_new_file

    @property
    def is_removed_file(self) -> bool:
        return self._fp.is_deleted_file

    @property
    def is_binary_file(self) -> bool:
        return self._fp.binary

    @property
    def is_rename(self) -> bool:
        has_from = any(h.kind == ExtendedHeaderKind.RENAME_FROM for h in self._fp.extended_headers)
        has_to = any(h.kind == ExtendedHeaderKind.RENAME_TO for h in self._fp.extended_headers)
        return has_from and has_to


def _compat_patch_files(patch_set: PatchSet) -> list[_CompatPatchedFile]:
    return [_CompatPatchedFile(fp) for fp in patch_set.files]


def _modified_files(files: ta.Iterable[_CompatPatchedFile]) -> list[_CompatPatchedFile]:
    return [fp for fp in files if not fp.is_added_file and not fp.is_removed_file]


def _added_files(files: ta.Iterable[_CompatPatchedFile]) -> list[_CompatPatchedFile]:
    return [fp for fp in files if fp.is_added_file]


def _removed_files(files: ta.Iterable[_CompatPatchedFile]) -> list[_CompatPatchedFile]:
    return [fp for fp in files if fp.is_removed_file]


def _render_hunk_line_value(hl: HunkLine) -> str:
    return hl.text if hl.has_no_newline_marker else (hl.text + '\n')
