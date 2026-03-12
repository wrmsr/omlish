# @omlish-llm-author "gpt-5.4-thinking"
import dataclasses as dc
import enum


##
# ast


class HunkLineKind(enum.StrEnum):
    CONTEXT = 'context'
    ADD = 'add'
    REMOVE = 'remove'


class ExtendedHeaderKind(enum.StrEnum):
    DIFF_GIT = 'diff_git'
    INDEX = 'index'
    OLD_MODE = 'old_mode'
    NEW_MODE = 'new_mode'
    DELETED_FILE_MODE = 'deleted_file_mode'
    NEW_FILE_MODE = 'new_file_mode'
    COPY_FROM = 'copy_from'
    COPY_TO = 'copy_to'
    RENAME_FROM = 'rename_from'
    RENAME_TO = 'rename_to'
    SIMILARITY_INDEX = 'similarity_index'
    DISSIMILARITY_INDEX = 'dissimilarity_index'
    BINARY_FILES = 'binary_files'
    GIT_BINARY_PATCH = 'git_binary_patch'
    UNKNOWN = 'unknown'


@dc.dataclass(frozen=True)
class SourceSpan:
    start_line: int
    end_line: int


@dc.dataclass(frozen=True)
class ExtendedHeader:
    kind: ExtendedHeaderKind
    text: str
    span: SourceSpan


@dc.dataclass(frozen=True)
class DiffGitHeader(ExtendedHeader):
    old_path: str
    new_path: str


@dc.dataclass(frozen=True)
class IndexHeader(ExtendedHeader):
    old_hash: str
    new_hash: str
    mode: str | None


@dc.dataclass(frozen=True)
class ModeHeader(ExtendedHeader):
    mode: str


@dc.dataclass(frozen=True)
class PathHeader(ExtendedHeader):
    path: str


@dc.dataclass(frozen=True)
class ScoreHeader(ExtendedHeader):
    score: int


@dc.dataclass(frozen=True)
class BinaryFilesHeader(ExtendedHeader):
    old_path: str
    new_path: str


@dc.dataclass(frozen=True)
class GitBinaryPatchHeader(ExtendedHeader):
    pass


@dc.dataclass(frozen=True)
class FileHeader:
    prefix: str  # '---' or '+++'
    path: str
    timestamp: str | None
    raw_path: str
    text: str
    span: SourceSpan


@dc.dataclass(frozen=True)
class HunkLine:
    kind: HunkLineKind
    text: str
    has_no_newline_marker: bool = False
    span: SourceSpan | None = None

    @property
    def is_context(self) -> bool:
        return self.kind == HunkLineKind.CONTEXT

    @property
    def is_add(self) -> bool:
        return self.kind == HunkLineKind.ADD

    @property
    def is_remove(self) -> bool:
        return self.kind == HunkLineKind.REMOVE


@dc.dataclass(frozen=True)
class Hunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    section: str | None
    lines: tuple[HunkLine, ...]
    text: str
    span: SourceSpan

    @property
    def added_count(self) -> int:
        return sum(1 for ln in self.lines if ln.kind == HunkLineKind.ADD)

    @property
    def removed_count(self) -> int:
        return sum(1 for ln in self.lines if ln.kind == HunkLineKind.REMOVE)

    @property
    def context_count(self) -> int:
        return sum(1 for ln in self.lines if ln.kind == HunkLineKind.CONTEXT)


@dc.dataclass(frozen=True, slots=True)
class GitBinaryPatchRecord:
    kind: str  # 'literal' or 'delta'
    size: int
    payload_lines: tuple[str, ...]
    span: SourceSpan


@dc.dataclass(frozen=True, slots=True)
class GitBinaryPatchData:
    records: tuple[GitBinaryPatchRecord, ...]
    span: SourceSpan

    @property
    def lines(self) -> tuple[str, ...]:
        out: list[str] = []
        for rec in self.records:
            out.append(f'{rec.kind} {rec.size}')
            out.extend(rec.payload_lines)
        return tuple(out)

    @property
    def byte_length(self) -> int:
        return sum(len(s) for s in self.lines)


@dc.dataclass(frozen=True)
class FilePatch:
    extended_headers: tuple[ExtendedHeader, ...]
    old_file: FileHeader | None
    new_file: FileHeader | None
    hunks: tuple[Hunk, ...]
    binary: bool
    git_binary_patch: GitBinaryPatchData | None
    span: SourceSpan

    @property
    def old_path(self) -> str | None:
        if self.old_file is not None:
            if self.old_file.path == '/dev/null':
                return None
            return self.old_file.path
        for hdr in self.extended_headers:
            if isinstance(hdr, DiffGitHeader):
                return hdr.old_path
            if isinstance(hdr, BinaryFilesHeader):
                return hdr.old_path
        return None

    @property
    def new_path(self) -> str | None:
        if self.new_file is not None:
            if self.new_file.path == '/dev/null':
                return None
            return self.new_file.path
        for hdr in self.extended_headers:
            if isinstance(hdr, DiffGitHeader):
                return hdr.new_path
            if isinstance(hdr, BinaryFilesHeader):
                return hdr.new_path
        return None

    @property
    def is_new_file(self) -> bool:
        return (
            any(h.kind == ExtendedHeaderKind.NEW_FILE_MODE for h in self.extended_headers)
            or (self.old_file is not None and self.old_file.path == '/dev/null')
        )

    @property
    def is_deleted_file(self) -> bool:
        return (
            any(h.kind == ExtendedHeaderKind.DELETED_FILE_MODE for h in self.extended_headers)
            or (self.new_file is not None and self.new_file.path == '/dev/null')
        )

    @property
    def added_count(self) -> int:
        return sum(h.added_count for h in self.hunks)

    @property
    def removed_count(self) -> int:
        return sum(h.removed_count for h in self.hunks)


@dc.dataclass(frozen=True, slots=True)
class PatchSet:
    preamble_lines: tuple[str, ...]
    files: tuple[FilePatch, ...]
    span: SourceSpan

    @property
    def added_count(self) -> int:
        return sum(fp.added_count for fp in self.files)

    @property
    def removed_count(self) -> int:
        return sum(fp.removed_count for fp in self.files)
