import collections.abc
import io
import typing as ta

from .. import check
from .. import collections as col
from .. import dataclasses as dc
from .. import dispatch
from .. import lang


T = ta.TypeVar('T')


Part: ta.TypeAlias = ta.Union[str, ta.Sequence['Part'], 'DataPart']
PartT = ta.TypeVar('PartT', bound=Part)


##


def _check_part(o: PartT) -> PartT:
    if isinstance(o, (str, DataPart)):
        pass
    elif isinstance(o, ta.Sequence):
        for c in o:
            _check_part(c)
    else:
        raise TypeError(o)
    return o


def _check_optional_part(o: ta.Optional[PartT]) -> ta.Optional[PartT]:
    if o is None:
        return None
    return _check_part(o)


##


class DataPart(dc.Frozen, lang.Abstract):
    pass


class Wrap(DataPart, lang.Final):
    part: Part = dc.xfield(coerce=_check_part)
    wrapper: tuple[str, str] = ('(', ')')


class List(DataPart, lang.Final):
    parts: ta.Sequence[ta.Optional[Part]] = dc.xfield(coerce=col.seq_of(_check_optional_part))
    delimiter: str = dc.field(default=',')  # FIXME: , check_type=str)
    trailer: bool = dc.field(default=False)  # FIXME: , check_type=bool)


class Concat(DataPart, lang.Final):
    parts: ta.Sequence[Part] = dc.xfield(coerce=col.seq_of(_check_part))


class Block(DataPart, lang.Final):
    parts: ta.Sequence[Part] = dc.xfield(coerce=col.seq_of(_check_part))


class Section(DataPart, lang.Final):
    parts: ta.Sequence[Part] = dc.xfield(coerce=col.seq_of(_check_part))


class Meta(DataPart, lang.Final):
    node: ta.Any


##


class PartTransform:
    @dispatch.method
    def __call__(self, part: Part) -> Part:
        raise TypeError(part)

    @__call__.register
    def __call__str(self, part: str) -> Part:
        return part

    @__call__.register
    def __call__sequence(self, part: collections.abc.Sequence) -> Part:
        return [self(c) for c in part]

    @__call__.register
    def __call__wrap(self, part: Wrap) -> Part:
        return Wrap(self(part.part), part.wrapper)

    @__call__.register
    def __call__list(self, part: List) -> Part:
        return List([self(c) for c in part.parts], part.delimiter, part.trailer)

    @__call__.register
    def __call__concat(self, part: Concat) -> Part:
        return Concat([self(c) for c in part.parts])

    @__call__.register
    def __call__block(self, part: Block) -> Part:
        return Block([self(c) for c in part.parts])

    @__call__.register
    def __call__section(self, part: Section) -> Part:
        return Section([self(c) for c in part.parts])

    @__call__.register
    def __call__meta(self, part: Meta) -> Meta:
        return part


##


class RemoveMetas(PartTransform):

    @PartTransform.__call__.register
    def __call__meta(self, part: Meta) -> Part:
        return []


remove_metas = RemoveMetas()


##


def _drop_empties(it: ta.Iterable[T]) -> list[T]:
    return [
        e  # type: ignore
        for e in it
        if not (
            isinstance(e, collections.abc.Sequence) and
            not e and
            not isinstance(e, str)
        )
    ]


class CompactPart(PartTransform):

    @PartTransform.__call__.register
    def __call__sequence(self, part: collections.abc.Sequence) -> Part:
        return _drop_empties(self(c) for c in part)

    @PartTransform.__call__.register
    def __call__list(self, part: List) -> Part:
        parts = _drop_empties(self(c) for c in part.parts)
        return List(parts, part.delimiter, part.trailer) if parts else []

    @PartTransform.__call__.register
    def __call__concat(self, part: Concat) -> Part:
        parts = _drop_empties(self(c) for c in part.parts)
        return Concat(parts) if parts else []

    @PartTransform.__call__.register
    def __call__block(self, part: Block) -> Part:
        parts = _drop_empties(self(c) for c in part.parts)
        return Block(parts) if parts else []

    @PartTransform.__call__.register
    def __call__section(self, part: Section) -> Part:
        parts = _drop_empties(self(c) for c in part.parts)
        return Section(parts) if parts else []


compact_part = CompactPart()


##


class PartRenderer:
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

    @dispatch.method
    def __call__(self, part: Part) -> None:
        raise TypeError(part)

    @__call__.register
    def __call__str(self, part: str) -> None:
        self._write(part)

    @__call__.register
    def __call__sequence(self, part: collections.abc.Sequence) -> None:
        for i, c in enumerate(part):
            if i:
                self._write(' ')
            self(c)

    @__call__.register
    def __call__wrap(self, part: Wrap) -> None:
        self._write(part.wrapper[0])
        self(part.part)
        self._write(part.wrapper[1])

    @__call__.register
    def __call__list(self, part: List) -> None:
        for i, c in enumerate(part.parts):
            if i:
                self._write(part.delimiter + ' ')
            self(c)
        if part.trailer:
            self._write(part.delimiter)

    @__call__.register
    def __call__concat(self, part: Concat) -> None:
        for c in part.parts:
            self(c)

    @__call__.register
    def __call__block(self, part: Block) -> None:
        for c in part.parts:
            self(c)
            self._write_newline()

    @__call__.register
    def __call__section(self, part: Section) -> None:
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
    part = remove_metas(part)
    part = compact_part(part)
    return render_part(part).getvalue()
