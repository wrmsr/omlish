import ast
import dis
import inspect
import linecache
import types
import typing as ta

from omlish import check


class Foo:
    def __init__(self):
        pass

    @classmethod
    def bar(cls):
        def baz():
            pass

        return baz


class SourcePosition(ta.NamedTuple):
    line: int
    column: int


def get_source_file_lines(
        filename: str,
        *,
        module_globals: ta.Mapping[str, ta.Any] | None = None,
) -> ta.Sequence[str]:
    def get_lines():
        return linecache.getlines(filename, module_globals)

    entry = linecache.cache.get(filename)
    linecache.checkcache(filename)
    lines = get_lines()
    if entry is not None and not lines:
        # There was an entry, checkcache removed it, and nothing replaced it. This means the file wasn't simply changed
        # (because the `lines` wouldn't be empty) but rather the file was found not to exist, probably because
        # `filename` was fake. Restore the original entry so that we still have something.
        linecache.cache[filename] = entry
        lines = get_lines()

    return lines


def build_code_pos_map(code: types.CodeType) -> dict[SourcePosition, list[dis.Instruction]]:
    instrs = list(dis.get_instructions(code))
    dct: dict[SourcePosition, list[dis.Instruction]] = {}
    for instr in instrs:
        if (
                (ip := instr.positions) is None or
                (line := ip.lineno) is None or
                (column := ip.col_offset) is None
        ):
            continue
        pos = SourcePosition(line, column)  # noqa
        dct.setdefault(pos, []).append(instr)
    return dct


def build_ast_pos_map(root: ast.AST) -> dict[SourcePosition, list[ast.AST]]:
    dct: dict[SourcePosition, list[ast.AST]] = {}
    for node in ast.walk(root):
        if (
                (ip := getattr(node, 'lineno', None)) is None or
                (column := getattr(node, 'col_offset', None)) is None
        ):
            continue
        pos = SourcePosition(ip, column)  # noqa
        dct.setdefault(pos, []).append(node)
    return dct


def find_source(code: types.CodeType) -> ta.Any:
    code_map = build_code_pos_map(code)

    source_file = inspect.getsourcefile(code)
    source_lines = get_source_file_lines(source_file)
    file_ast = ast.parse(''.join(source_lines))

    ast_map = build_ast_pos_map(file_ast)

    print()


def _main() -> None:
    find_source(Foo.bar().__code__)


if __name__ == '__main__':
    _main()
