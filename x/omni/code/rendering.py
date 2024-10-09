import collections.abc
import io
import typing as ta

from .. import check
from .. import collections as col
from .. import dataclasses as dc
from .. import dispatch


T = ta.TypeVar('T')
NodeT = ta.TypeVar('NodeT')


Part = ta.Union[str, ta.Sequence['Part'], 'DataPart']
PartT = ta.TypeVar('PartT', bound=Part)


def _check_part(o: PartT) -> PartT:
    if isinstance(o, (str, DataPart)):
        pass
    elif isinstance(o, ta.Sequence):
        for c in o:
            _check_part(c)
    else:
        raise TypeError(o)
    return o


class DataPart(dc.Enum):
    pass


class Wrap(DataPart):
    part: Part = dc.field(coerce=_check_part)
    wrapper: ta.Tuple[str, str] = ('(', ')')


class List(DataPart):
    parts: ta.Sequence[ta.Optional[Part]] = dc.field(coerce=col.seq_of(_check_part))
    delimiter: str = dc.field(',', check_type=str)
    trailer: bool = dc.field(False, check_type=bool)


class Concat(DataPart):
    parts: ta.Sequence[Part] = dc.field(coerce=col.seq_of(_check_part))


class Block(DataPart):
    parts: ta.Sequence[Part] = dc.field(coerce=col.seq_of(_check_part))


class Section(DataPart):
    parts: ta.Sequence[Part] = dc.field(coerce=col.seq_of(_check_part))


class Node(DataPart, ta.Generic[NodeT], final=False):
    node: NodeT


class PartTransform(dispatch.Class):
    __call__ = dispatch.property()

    def __call__(self, part: str) -> Part:  # noqa
        return part

    def __call__(self, part: collections.abc.Sequence) -> Part:  # noqa
        return [self(c) for c in part]

    def __call__(self, part: Wrap) -> Part:  # noqa
        return Wrap(self(part.part), part.wrapper)

    def __call__(self, part: List) -> Part:  # noqa
        return List([self(c) for c in part.parts], part.delimiter, part.trailer)

    def __call__(self, part: Concat) -> Part:  # noqa
        return Concat([self(c) for c in part.parts])

    def __call__(self, part: Block) -> Part:  # noqa
        return Block([self(c) for c in part.parts])

    def __call__(self, part: Section) -> Part:  # noqa
        return Section([self(c) for c in part.parts])

    def __call__(self, part: Node) -> Part:  # noqa
        return part


class RemoveNodes(PartTransform):

    def __call__(self, part: Node) -> Part:  # noqa
        return []


remove_nodes = RemoveNodes()


def _drop_empties(it: ta.Iterable[T]) -> ta.List[T]:
    return [
        e for e in it if not (
                isinstance(e, collections.abc.Sequence) and
                not e and
                not isinstance(e, str)
        )
    ]


class CompactPart(PartTransform):

    def __call__(self, part: collections.abc.Sequence) -> Part:  # noqa
        return _drop_empties(self(c) for c in part)

    def __call__(self, part: List) -> Part:  # noqa
        parts = _drop_empties(self(c) for c in part.parts)
        return List(parts, part.delimiter, part.trailer) if parts else []

    def __call__(self, part: Concat) -> Part:  # noqa
        parts = _drop_empties(self(c) for c in part.parts)
        return Concat(parts) if parts else []

    def __call__(self, part: Block) -> Part:  # noqa
        parts = _drop_empties(self(c) for c in part.parts)
        return Block(parts) if parts else []

    def __call__(self, part: Section) -> Part:  # noqa
        parts = _drop_empties(self(c) for c in part.parts)
        return Section(parts) if parts else []


compact_part = CompactPart()


class PartRenderer(dispatch.Class):
    def __init__(self, buf: io.StringIO, *, indent: str = '    ') -> None:
        super().__init__()

        self._buf = buf

        self._indents = 0
        self._indent = indent

        self._blank_lines = 0
        self._has_indented = False

    def _write(self, s: str) -> None:
        check.not_in('\n', s)
        if not self._has_indented:
            self._buf.write(self._indent * self._indents)
            self._blank_lines = 0
            self._has_indented = True

        self._buf.write(s)

    def _write_newline(self, n: int = 1) -> None:
        check.arg(n >= 0)
        d = n - self._blank_lines
        if d > 0:
            self._buf.write('\n' * n)
            self._blank_lines += n
            self._has_indented = False

    __call__ = dispatch.property()

    def __call__(self, part: str) -> None:  # noqa
        self._write(part)

    def __call__(self, part: collections.abc.Sequence) -> None:  # noqa
        for i, c in enumerate(part):
            if i:
                self._write(' ')
            self(c)

    def __call__(self, part: DataPart) -> None:  # noqa
        raise TypeError(part)

    def __call__(self, part: Wrap) -> None:  # noqa
        self._write(part.wrapper[0])
        self(part.part)
        self._write(part.wrapper[1])

    def __call__(self, part: List) -> None:  # noqa
        for i, c in enumerate(part.parts):
            if i:
                self._write(part.delimiter + ' ')
            self(c)
        if part.trailer:
            self._write(part.delimiter)

    def __call__(self, part: Concat) -> None:  # noqa
        for c in part.parts:
            self(c)

    def __call__(self, part: Block) -> None:  # noqa
        for c in part.parts:
            self(c)
            self._write_newline()

    def __call__(self, part: Section) -> None:  # noqa
        self._indents += 1
        try:
            for c in part.parts:
                self(c)
        finally:
            self._indents -= 1


def render_part(part: Part, buf: ta.Optional[io.StringIO] = None) -> io.StringIO:
    if buf is None:
        buf = io.StringIO()
    PartRenderer(buf)(part)
    return buf


def render(part: Part) -> str:
    part = remove_nodes(part)  # noqa
    part = compact_part(part)
    return render_part(part).getvalue()
