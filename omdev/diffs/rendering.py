# @omlish-llm-author "gpt-5.4-thinking"
import dataclasses as dc

from .types import BinaryFilesHeader
from .types import DiffGitHeader
from .types import ExtendedHeader
from .types import ExtendedHeaderKind
from .types import FileHeader
from .types import FilePatch
from .types import GitBinaryPatchData
from .types import GitBinaryPatchHeader
from .types import Hunk
from .types import HunkLine
from .types import HunkLineKind
from .types import IndexHeader
from .types import ModeHeader
from .types import PatchSet
from .types import PathHeader
from .types import ScoreHeader


##


@dc.dataclass(frozen=True, slots=True)
class PatchRenderOptions:
    trailing_newline: bool = True


class PatchSetRenderer:
    def __init__(self, options: PatchRenderOptions | None = None) -> None:
        super().__init__()

        self._options = options or PatchRenderOptions()

    def render_patch_set(self, patch: PatchSet) -> str:
        parts: list[str] = []

        for line in patch.preamble_lines:
            parts.append(f'{line}\n')

        for fp in patch.files:
            parts.append(self.render_file_patch(fp))

        out = ''.join(parts)
        if self._options.trailing_newline and out and not out.endswith('\n'):
            out += '\n'
        return out

    def render_file_patch(self, fp: FilePatch) -> str:
        parts: list[str] = []

        for hdr in fp.extended_headers:
            parts.append(self.render_extended_header(hdr))

        if fp.old_file is not None:
            parts.append(self.render_file_header(fp.old_file))
        if fp.new_file is not None:
            parts.append(self.render_file_header(fp.new_file))

        if fp.git_binary_patch is not None:
            parts.append(self.render_git_binary_patch_data(fp.git_binary_patch))

        for hunk in fp.hunks:
            parts.append(self.render_hunk(hunk))

        return ''.join(parts)

    def render_extended_header(self, hdr: ExtendedHeader) -> str:
        match hdr:
            case DiffGitHeader(old_path=old_path, new_path=new_path):
                return f'diff --git a/{old_path} b/{new_path}\n'

            case IndexHeader(old_hash=old_hash, new_hash=new_hash, mode=mode):
                if mode is not None:
                    return f'index {old_hash}..{new_hash} {mode}\n'
                return f'index {old_hash}..{new_hash}\n'

            case ModeHeader(kind=kind, mode=mode):
                match kind:
                    case ExtendedHeaderKind.OLD_MODE:
                        return f'old mode {mode}\n'
                    case ExtendedHeaderKind.NEW_MODE:
                        return f'new mode {mode}\n'
                    case ExtendedHeaderKind.DELETED_FILE_MODE:
                        return f'deleted file mode {mode}\n'
                    case ExtendedHeaderKind.NEW_FILE_MODE:
                        return f'new file mode {mode}\n'
                    case _:
                        raise ValueError(f'unexpected mode header kind: {kind}')

            case PathHeader(kind=kind, path=path):
                match kind:
                    case ExtendedHeaderKind.COPY_FROM:
                        return f'copy from {path}\n'
                    case ExtendedHeaderKind.COPY_TO:
                        return f'copy to {path}\n'
                    case ExtendedHeaderKind.RENAME_FROM:
                        return f'rename from {path}\n'
                    case ExtendedHeaderKind.RENAME_TO:
                        return f'rename to {path}\n'
                    case _:
                        raise ValueError(f'unexpected path header kind: {kind}')

            case ScoreHeader(kind=kind, score=score):
                match kind:
                    case ExtendedHeaderKind.SIMILARITY_INDEX:
                        return f'similarity index {score}%\n'
                    case ExtendedHeaderKind.DISSIMILARITY_INDEX:
                        return f'dissimilarity index {score}%\n'
                    case _:
                        raise ValueError(f'unexpected score header kind: {kind}')

            case BinaryFilesHeader(old_path=old_path, new_path=new_path):
                return f'Binary files {old_path} and {new_path} differ\n'

            case GitBinaryPatchHeader():
                return 'GIT binary patch\n'

            case ExtendedHeader(text=text):
                return f'{text}\n'

            case _:
                raise TypeError(type(hdr))

    def render_file_header(self, hdr: FileHeader) -> str:
        if hdr.timestamp is not None:
            return f'{hdr.prefix} {hdr.raw_path}\t{hdr.timestamp}\n'
        return f'{hdr.prefix} {hdr.raw_path}\n'

    def render_hunk(self, hunk: Hunk) -> str:
        parts: list[str] = []
        parts.append(self.render_hunk_header(hunk))

        for ln in hunk.lines:
            parts.append(self.render_hunk_line(ln))
            if ln.has_no_newline_marker:
                parts.append('\\ No newline at end of file\n')

        return ''.join(parts)

    def render_hunk_header(self, hunk: Hunk) -> str:
        old_range = self._render_hunk_range(hunk.old_start, hunk.old_count)
        new_range = self._render_hunk_range(hunk.new_start, hunk.new_count)
        if hunk.section:
            return f'@@ -{old_range} +{new_range} @@ {hunk.section}\n'
        return f'@@ -{old_range} +{new_range} @@\n'

    @staticmethod
    def _render_hunk_range(start: int, count: int) -> str:
        if count == 1:
            return f'{start}'
        return f'{start},{count}'

    def render_hunk_line(self, ln: HunkLine) -> str:
        match ln.kind:
            case HunkLineKind.CONTEXT:
                prefix = ' '
            case HunkLineKind.ADD:
                prefix = '+'
            case HunkLineKind.REMOVE:
                prefix = '-'
            case _:
                raise ValueError(ln.kind)

        return f'{prefix}{ln.text}\n'

    def render_git_binary_patch_data(self, data: GitBinaryPatchData) -> str:
        parts: list[str] = []

        for rec in data.records:
            parts.append(f'{rec.kind} {rec.size}\n')
            for line in rec.payload_lines:
                parts.append(f'{line}\n')

        return ''.join(parts)
