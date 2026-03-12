# @omlish-llm-author "gpt-5.4-thinking"
# @omlish-precheck-allow-any-unicode
import dataclasses as dc
import re
import typing as ta

from .types import BinaryFilesHeader
from .types import DiffGitHeader
from .types import ExtendedHeader
from .types import ExtendedHeaderKind
from .types import FileHeader
from .types import FilePatch
from .types import GitBinaryPatchData
from .types import GitBinaryPatchHeader
from .types import GitBinaryPatchRecord
from .types import Hunk
from .types import HunkLine
from .types import HunkLineKind
from .types import IndexHeader
from .types import ModeHeader
from .types import PatchSet
from .types import PathHeader
from .types import ScoreHeader
from .types import SourceSpan


##


class DiffParseError(Exception):
    pass


##


_RE_DIFF_GIT = re.compile(r'^diff --git a/(.+) b/(.+)$')
_RE_INDEX = re.compile(r'^index ([0-9A-Fa-f]+)\.\.([0-9A-Fa-f]+)(?: ([0-7]{6}))?$')
_RE_OLD_MODE = re.compile(r'^old mode ([0-7]{6})$')
_RE_NEW_MODE = re.compile(r'^new mode ([0-7]{6})$')
_RE_DELETED_FILE_MODE = re.compile(r'^deleted file mode ([0-7]{6})$')
_RE_NEW_FILE_MODE = re.compile(r'^new file mode ([0-7]{6})$')
_RE_COPY_FROM = re.compile(r'^copy from (.+)$')
_RE_COPY_TO = re.compile(r'^copy to (.+)$')
_RE_RENAME_FROM = re.compile(r'^rename from (.+)$')
_RE_RENAME_TO = re.compile(r'^rename to (.+)$')
_RE_SIMILARITY_INDEX = re.compile(r'^similarity index (\d+)%$')
_RE_DISSIMILARITY_INDEX = re.compile(r'^dissimilarity index (\d+)%$')
_RE_BINARY_FILES = re.compile(r'^Binary files (.+) and (.+) differ$')
_RE_FILE_HEADER = re.compile(r'^(---|\+\+\+) (.+?)(?:\t(.*))?$')
_RE_HUNK_HEADER = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?: ?(.*))?$')
_RE_NO_NEWLINE = re.compile(r'^\\ No newline at end of file$')
_RE_GIT_BINARY_LITERAL = re.compile(r'^(literal|delta) (\d+)$')
_RE_GIT_BINARY_RECORD = re.compile(r'^(literal|delta) (\d+)$')


class _PatchParser:
    def __init__(self, text: str) -> None:
        super().__init__()

        self._text = text
        self._lines = text.splitlines(keepends=True)
        self._i = 0

    def parse(self) -> PatchSet:
        preamble_lines: list[str] = []
        files: list[FilePatch] = []
        seen_first_file_patch = False

        while self._i < len(self._lines):
            if not seen_first_file_patch:
                fp = self._parse_maybe_file_patch()
                if fp is None:
                    preamble_lines.append(self._next_line_raw().rstrip('\r\n'))
                    continue
                files.append(fp)
                seen_first_file_patch = True
                continue

            if self._is_ignorable_top_level_line(self._peek_line_stripped()):
                self._i += 1
                continue

            fp = self._parse_maybe_file_patch()
            if fp is None:
                raise DiffParseError(...)
            files.append(fp)

        end = len(self._lines) if self._lines else 0
        return PatchSet(
            preamble_lines=tuple(preamble_lines),
            files=tuple(files),
            span=SourceSpan(1 if end else 0, end),
        )

    def _parse_maybe_file_patch(self) -> FilePatch | None:
        start_i = self._i

        extended_headers: list[ExtendedHeader] = []
        old_file: FileHeader | None = None
        new_file: FileHeader | None = None
        hunks: list[Hunk] = []
        git_binary_patch: GitBinaryPatchData | None = None
        binary = False

        saw_diff_git = False

        if self._peek_is_diff_git():
            extended_headers.append(self._parse_extended_header())
            saw_diff_git = True

        while self._i < len(self._lines):
            s = self._peek_line_stripped()

            if s == '':
                break

            if self._peek_is_file_header('---') or self._peek_is_hunk_header():
                break

            if s == 'GIT binary patch':
                hdr = self._parse_extended_header()
                extended_headers.append(hdr)
                binary = True
                git_binary_patch = self._parse_git_binary_patch_data()
                break

            if saw_diff_git:
                hdr = self._parse_extended_header()
                extended_headers.append(hdr)
                if hdr.kind == ExtendedHeaderKind.BINARY_FILES:
                    binary = True
                continue

            if self._is_extended_header_line(s):
                hdr = self._parse_extended_header()
                extended_headers.append(hdr)
                if hdr.kind == ExtendedHeaderKind.BINARY_FILES:
                    binary = True
                continue

            break

        if self._peek_is_file_header('---'):
            old_file = self._parse_file_header('---')
            if not self._peek_is_file_header('+++'):
                ln = self._line_no()
                raise DiffParseError(f'expected +++ file header after --- at line {ln}')
            new_file = self._parse_file_header('+++')

        binary = binary or any(
            h.kind in (ExtendedHeaderKind.BINARY_FILES, ExtendedHeaderKind.GIT_BINARY_PATCH)
            for h in extended_headers
        )

        while self._peek_is_hunk_header():
            hunks.append(self._parse_hunk())

        if not extended_headers and old_file is None and new_file is None and not hunks:
            self._i = start_i
            return None

        if old_file is None and new_file is None and not binary:
            ln = self._line_no()
            raise DiffParseError(f'file patch missing ---/+++ headers or binary marker at line {ln}')

        end_i = self._i
        return FilePatch(
            extended_headers=tuple(extended_headers),
            old_file=old_file,
            new_file=new_file,
            hunks=tuple(hunks),
            binary=binary,
            git_binary_patch=git_binary_patch,
            span=SourceSpan(start_i + 1, end_i),
        )

    def _parse_extended_header(self) -> ExtendedHeader:
        line = self._next_line_raw()
        s = line.rstrip('\r\n')
        span = SourceSpan(self._i, self._i)

        if (m := _RE_DIFF_GIT.match(s)) is not None:
            return DiffGitHeader(
                kind=ExtendedHeaderKind.DIFF_GIT,
                text=s,
                span=span,
                old_path=m.group(1),
                new_path=m.group(2),
            )

        if (m := _RE_INDEX.match(s)) is not None:
            return IndexHeader(
                kind=ExtendedHeaderKind.INDEX,
                text=s,
                span=span,
                old_hash=m.group(1),
                new_hash=m.group(2),
                mode=m.group(3),
            )

        if (m := _RE_OLD_MODE.match(s)) is not None:
            return ModeHeader(
                kind=ExtendedHeaderKind.OLD_MODE,
                text=s,
                span=span,
                mode=m.group(1),
            )

        if (m := _RE_NEW_MODE.match(s)) is not None:
            return ModeHeader(
                kind=ExtendedHeaderKind.NEW_MODE,
                text=s,
                span=span,
                mode=m.group(1),
            )

        if (m := _RE_DELETED_FILE_MODE.match(s)) is not None:
            return ModeHeader(
                kind=ExtendedHeaderKind.DELETED_FILE_MODE,
                text=s,
                span=span,
                mode=m.group(1),
            )

        if (m := _RE_NEW_FILE_MODE.match(s)) is not None:
            return ModeHeader(
                kind=ExtendedHeaderKind.NEW_FILE_MODE,
                text=s,
                span=span,
                mode=m.group(1),
            )

        if (m := _RE_COPY_FROM.match(s)) is not None:
            return PathHeader(
                kind=ExtendedHeaderKind.COPY_FROM,
                text=s,
                span=span,
                path=m.group(1),
            )

        if (m := _RE_COPY_TO.match(s)) is not None:
            return PathHeader(
                kind=ExtendedHeaderKind.COPY_TO,
                text=s,
                span=span,
                path=m.group(1),
            )

        if (m := _RE_RENAME_FROM.match(s)) is not None:
            return PathHeader(
                kind=ExtendedHeaderKind.RENAME_FROM,
                text=s,
                span=span,
                path=m.group(1),
            )

        if (m := _RE_RENAME_TO.match(s)) is not None:
            return PathHeader(
                kind=ExtendedHeaderKind.RENAME_TO,
                text=s,
                span=span,
                path=m.group(1),
            )

        if (m := _RE_SIMILARITY_INDEX.match(s)) is not None:
            return ScoreHeader(
                kind=ExtendedHeaderKind.SIMILARITY_INDEX,
                text=s,
                span=span,
                score=int(m.group(1)),
            )

        if (m := _RE_DISSIMILARITY_INDEX.match(s)) is not None:
            return ScoreHeader(
                kind=ExtendedHeaderKind.DISSIMILARITY_INDEX,
                text=s,
                span=span,
                score=int(m.group(1)),
            )

        if (m := _RE_BINARY_FILES.match(s)) is not None:
            return BinaryFilesHeader(
                kind=ExtendedHeaderKind.BINARY_FILES,
                text=s,
                span=span,
                old_path=m.group(1),
                new_path=m.group(2),
            )

        if s == 'GIT binary patch':
            return GitBinaryPatchHeader(
                kind=ExtendedHeaderKind.GIT_BINARY_PATCH,
                text=s,
                span=span,
            )

        return ExtendedHeader(
            kind=ExtendedHeaderKind.UNKNOWN,
            text=s,
            span=span,
        )

    def _parse_file_header(self, prefix: str) -> FileHeader:
        line = self._next_line_raw()
        s = line.rstrip('\r\n')
        span = SourceSpan(self._i, self._i)

        m = _RE_FILE_HEADER.match(s)
        if m is None or m.group(1) != prefix:
            raise DiffParseError(f'expected {prefix} file header at line {self._i}')

        raw_path = m.group(2)
        timestamp = m.group(3)
        path = self._normalize_patch_path(raw_path)

        return FileHeader(
            prefix=prefix,
            path=path,
            timestamp=timestamp,
            raw_path=raw_path,
            text=s,
            span=span,
        )

    def _parse_hunk(self) -> Hunk:
        header_line_no = self._line_no()
        header_line = self._next_line_raw()
        header_s = header_line.rstrip('\r\n')
        m = _RE_HUNK_HEADER.match(header_s)
        if m is None:
            raise DiffParseError(f'expected hunk header at line {header_line_no}')

        old_start = int(m.group(1))
        old_count = int(m.group(2)) if m.group(2) else 1
        new_start = int(m.group(3))
        new_count = int(m.group(4)) if m.group(4) else 1
        section = m.group(5) or None

        lines: list[HunkLine] = []
        hunk_start_i = self._i - 1

        seen_old = 0
        seen_new = 0

        while self._i < len(self._lines):
            s = self._peek_line_stripped()

            if self._peek_is_hunk_header():
                break
            if self._peek_is_next_file_boundary():
                break

            raw = self._peek_line_raw()

            if not raw:
                break

            c = raw[0]
            if c == ' ':
                line_no = self._line_no()
                self._i += 1
                lines.append(HunkLine(
                    kind=HunkLineKind.CONTEXT,
                    text=raw[1:].rstrip('\r\n'),
                    span=SourceSpan(line_no, line_no),
                ))
                seen_old += 1
                seen_new += 1
                continue

            if c == '+':
                line_no = self._line_no()
                self._i += 1
                lines.append(HunkLine(
                    kind=HunkLineKind.ADD,
                    text=raw[1:].rstrip('\r\n'),
                    span=SourceSpan(line_no, line_no),
                ))
                seen_new += 1
                continue

            if c == '-':
                line_no = self._line_no()
                self._i += 1
                lines.append(HunkLine(
                    kind=HunkLineKind.REMOVE,
                    text=raw[1:].rstrip('\r\n'),
                    span=SourceSpan(line_no, line_no),
                ))
                seen_old += 1
                continue

            if _RE_NO_NEWLINE.match(s) is not None:
                line_no = self._line_no()
                self._i += 1
                if not lines:
                    raise DiffParseError(f'orphaned no-newline marker at line {line_no}')
                prev = lines[-1]
                lines[-1] = HunkLine(
                    kind=prev.kind,
                    text=prev.text,
                    has_no_newline_marker=True,
                    span=prev.span,
                )
                continue

            raise DiffParseError(f'unrecognized hunk line at line {self._line_no()}: {s!r}')

        if seen_old != old_count:
            raise DiffParseError(
                f'hunk old-count mismatch at line {header_line_no}: header={old_count}, parsed={seen_old}',
            )
        if seen_new != new_count:
            raise DiffParseError(
                f'hunk new-count mismatch at line {header_line_no}: header={new_count}, parsed={seen_new}',
            )

        hunk_end_i = self._i
        hunk_text = ''.join(self._lines[hunk_start_i:hunk_end_i]).rstrip('\r\n')

        return Hunk(
            old_start=old_start,
            old_count=old_count,
            new_start=new_start,
            new_count=new_count,
            section=section,
            lines=tuple(lines),
            text=hunk_text,
            span=SourceSpan(hunk_start_i + 1, hunk_end_i),
        )

    def _peek_is_top_level_file_start(self) -> bool:
        if self._i >= len(self._lines):
            return False
        s = self._peek_line_stripped()
        return _RE_DIFF_GIT.match(s) is not None

    def _parse_git_binary_patch_data(self) -> GitBinaryPatchData:
        start_i = self._i
        records: list[GitBinaryPatchRecord] = []

        if self._i >= len(self._lines):
            raise DiffParseError('GIT binary patch missing payload')

        while self._i < len(self._lines):
            s = self._peek_line_stripped()

            if s == '':
                # Allow blank separator only before next file or EOF.
                if self._i + 1 >= len(self._lines):
                    self._i += 1
                    break
                nxt = self._lines[self._i + 1].rstrip('\r\n')
                if _RE_DIFF_GIT.match(nxt) is not None:
                    self._i += 1
                    break
                raise DiffParseError(f'unexpected blank line in git binary patch at line {self._line_no()}')

            if self._peek_is_top_level_file_start():
                # End of current binary patch, next file begins.
                break

            records.append(self._parse_git_binary_patch_record())

        if not records:
            raise DiffParseError('GIT binary patch contained no records')

        return GitBinaryPatchData(
            records=tuple(records),
            span=SourceSpan(start_i + 1, self._i),
        )

    def _parse_git_binary_patch_record(self) -> GitBinaryPatchRecord:
        header_line_no = self._line_no()
        s = self._peek_line_stripped()
        m = _RE_GIT_BINARY_RECORD.match(s)
        if m is None:
            raise DiffParseError(f'expected git binary patch record at line {header_line_no}: {s!r}')

        kind = m.group(1)
        size = int(m.group(2))
        self._i += 1

        payload_lines: list[str] = []

        while self._i < len(self._lines):
            s = self._peek_line_stripped()

            # Next record begins.
            if _RE_GIT_BINARY_RECORD.match(s) is not None:
                break

            # A top-level new file start is only legal between records, not mid-record.
            if self._peek_is_top_level_file_start():
                if not payload_lines:
                    raise DiffParseError(
                        f'git binary patch record at line {header_line_no} has no payload before next file',
                    )
                break

            if s == '':
                # Blank is only allowed between records / before next file, not inside payload.
                if self._i + 1 >= len(self._lines):
                    break
                nxt = self._lines[self._i + 1].rstrip('\r\n')
                if _RE_DIFF_GIT.match(nxt) is not None or _RE_GIT_BINARY_RECORD.match(nxt) is not None:
                    break
                raise DiffParseError(
                    f'unexpected blank line inside git binary patch record at line {self._line_no()}',
                )

            payload_lines.append(self._next_line_raw().rstrip('\r\n'))

        if not payload_lines:
            raise DiffParseError(f'git binary patch record at line {header_line_no} has empty payload')

        return GitBinaryPatchRecord(
            kind=kind,
            size=size,
            payload_lines=tuple(payload_lines),
            span=SourceSpan(header_line_no, self._i),
        )

    @staticmethod
    def _normalize_patch_path(raw_path: str) -> str:
        if raw_path == '/dev/null':
            return raw_path
        if raw_path.startswith('a/'):
            return raw_path[2:]
        if raw_path.startswith('b/'):
            return raw_path[2:]
        return raw_path

    def _peek_is_diff_git(self) -> bool:
        if self._i >= len(self._lines):
            return False
        return _RE_DIFF_GIT.match(self._peek_line_stripped()) is not None

    def _peek_is_file_header(self, prefix: str) -> bool:
        if self._i >= len(self._lines):
            return False
        s = self._peek_line_stripped()
        return s.startswith(prefix + ' ')

    def _peek_is_hunk_header(self) -> bool:
        if self._i >= len(self._lines):
            return False
        return _RE_HUNK_HEADER.match(self._peek_line_stripped()) is not None

    def _peek_is_next_file_boundary(self) -> bool:
        if self._i >= len(self._lines):
            return True
        s = self._peek_line_stripped()
        if s == '':
            return True
        if _RE_DIFF_GIT.match(s) is not None:
            return True
        if s.startswith('--- '):
            return True
        if _RE_BINARY_FILES.match(s) is not None:
            return True
        return False

    @staticmethod
    def _is_ignorable_top_level_line(s: str) -> bool:
        return s == ''

    @staticmethod
    def _is_extended_header_line(s: str) -> bool:
        return any((
            _RE_DIFF_GIT.match(s) is not None,
            _RE_INDEX.match(s) is not None,
            _RE_OLD_MODE.match(s) is not None,
            _RE_NEW_MODE.match(s) is not None,
            _RE_DELETED_FILE_MODE.match(s) is not None,
            _RE_NEW_FILE_MODE.match(s) is not None,
            _RE_COPY_FROM.match(s) is not None,
            _RE_COPY_TO.match(s) is not None,
            _RE_RENAME_FROM.match(s) is not None,
            _RE_RENAME_TO.match(s) is not None,
            _RE_SIMILARITY_INDEX.match(s) is not None,
            _RE_DISSIMILARITY_INDEX.match(s) is not None,
            _RE_BINARY_FILES.match(s) is not None,
            s == 'GIT binary patch',
        ))

    def _line_no(self) -> int:
        return self._i + 1

    def _peek_line_raw(self) -> str:
        return self._lines[self._i]

    def _peek_line_stripped(self) -> str:
        return self._lines[self._i].rstrip('\r\n')

    def _next_line_raw(self) -> str:
        line = self._lines[self._i]
        self._i += 1
        return line


##
# reconstruction helpers


@dc.dataclass(frozen=True)
class ReconstructedFileView:
    path: str | None
    lines: tuple[str, ...]
    missing_trailing_newline: bool


@dc.dataclass(frozen=True)
class ReconstructedFilePair:
    before: ReconstructedFileView
    after: ReconstructedFileView


def reconstruct_file_pair_from_hunks(file_patch: FilePatch) -> ReconstructedFilePair:
    """
    Reconstructs the *partial* before/after file views implied by the patch hunks.

    Important:
      - This does not recreate untouched file content outside hunks.
      - It fills hunk gaps with placeholder lines.
      - It is ideal for TUI display of "patch-local" before/after views.

    If you have the full original file contents, you should instead apply hunks to
    those contents for a true full-file reconstruction.
    """

    before_lines: list[str] = []
    after_lines: list[str] = []

    old_cursor = 1
    new_cursor = 1

    before_missing_nl = False
    after_missing_nl = False

    for hunk in file_patch.hunks:
        while old_cursor < hunk.old_start:
            before_lines.append(_gap_line(old_cursor))
            old_cursor += 1

        while new_cursor < hunk.new_start:
            after_lines.append(_gap_line(new_cursor))
            new_cursor += 1

        old_line_no = hunk.old_start
        new_line_no = hunk.new_start

        for hl in hunk.lines:
            match hl.kind:
                case HunkLineKind.CONTEXT:
                    before_lines.append(hl.text)
                    after_lines.append(hl.text)
                    old_cursor = old_line_no + 1
                    new_cursor = new_line_no + 1
                    old_line_no += 1
                    new_line_no += 1

                    if hl.has_no_newline_marker:
                        before_missing_nl = True
                        after_missing_nl = True

                case HunkLineKind.REMOVE:
                    before_lines.append(hl.text)
                    old_cursor = old_line_no + 1
                    old_line_no += 1

                    if hl.has_no_newline_marker:
                        before_missing_nl = True

                case HunkLineKind.ADD:
                    after_lines.append(hl.text)
                    new_cursor = new_line_no + 1
                    new_line_no += 1

                    if hl.has_no_newline_marker:
                        after_missing_nl = True

                case _:
                    raise AssertionError(hl.kind)

    return ReconstructedFilePair(
        before=ReconstructedFileView(
            path=file_patch.old_path,
            lines=tuple(before_lines),
            missing_trailing_newline=before_missing_nl,
        ),
        after=ReconstructedFileView(
            path=file_patch.new_path,
            lines=tuple(after_lines),
            missing_trailing_newline=after_missing_nl,
        ),
    )


def _gap_line(line_no: int) -> str:
    return f'…'


def apply_hunks_to_old_lines(
    file_patch: FilePatch,
    old_lines: ta.Sequence[str],
) -> ReconstructedFileView:
    """
    Given the full old file contents (without trailing newlines), apply this file patch
    to produce the new file contents.

    This is the helper you want when you *do* have the original file.
    """

    if file_patch.binary:
        raise ValueError('cannot apply binary patch')

    out: list[str] = []
    old_idx = 0
    missing_trailing_newline = False

    for hunk in file_patch.hunks:
        want_old_idx = hunk.old_start - 1

        if want_old_idx < old_idx:
            raise DiffParseError('overlapping hunks are not supported')

        while old_idx < want_old_idx:
            if old_idx >= len(old_lines):
                raise DiffParseError('hunk starts beyond end of old file')
            out.append(old_lines[old_idx])
            old_idx += 1

        for hl in hunk.lines:
            match hl.kind:
                case HunkLineKind.CONTEXT:
                    if old_idx >= len(old_lines):
                        raise DiffParseError('context line beyond end of old file')
                    if old_lines[old_idx] != hl.text:
                        raise DiffParseError(
                            f'context mismatch at old line {old_idx + 1}: '
                            f'expected {hl.text!r}, got {old_lines[old_idx]!r}',
                        )
                    out.append(old_lines[old_idx])
                    old_idx += 1
                    if hl.has_no_newline_marker:
                        missing_trailing_newline = True

                case HunkLineKind.REMOVE:
                    if old_idx >= len(old_lines):
                        raise DiffParseError('remove line beyond end of old file')
                    if old_lines[old_idx] != hl.text:
                        raise DiffParseError(
                            f'remove mismatch at old line {old_idx + 1}: '
                            f'expected {hl.text!r}, got {old_lines[old_idx]!r}',
                        )
                    old_idx += 1

                case HunkLineKind.ADD:
                    out.append(hl.text)
                    if hl.has_no_newline_marker:
                        missing_trailing_newline = True

                case _:
                    raise AssertionError(hl.kind)

    while old_idx < len(old_lines):
        out.append(old_lines[old_idx])
        old_idx += 1

    return ReconstructedFileView(
        path=file_patch.new_path,
        lines=tuple(out),
        missing_trailing_newline=missing_trailing_newline,
    )


def parse_patch(text: str) -> PatchSet:
    return _PatchParser(text).parse()
