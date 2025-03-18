import collections.abc
import io
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import dispatch


T = ta.TypeVar('T')


Part: ta.TypeAlias = ta.Union[str, ta.Sequence['Part'], 'DataPart']
PartT = ta.TypeVar('PartT', bound=Part)


##


def check_part(o: PartT) -> PartT:
    if isinstance(o, (str, DataPart)):
        pass
    elif isinstance(o, ta.Sequence):
        for c in o:
            check_part(c)
    else:
        raise TypeError(o)
    return o


def check_opt_part(o: PartT | None) -> PartT | None:
    if o is None:
        return None
    return check_part(o)


##


class DataPart(dc.Case):
    pass


class Wrap(DataPart):
    part: Part
    wrapper: tuple[str, str] = ('(', ')')


class List(DataPart):
    parts: ta.Sequence[Part | None]
    delimiter: str = ','  # FIXME: Part
    trailer: bool = False


class Concat(DataPart):
    parts: ta.Sequence[Part]


class Block(DataPart):
    parts: ta.Sequence[Part]


class Section(DataPart):
    parts: ta.Sequence[Part]


class Meta(DataPart):
    node: ta.Any


##


class PartTransform:
    def __call__(self, part: Part | None) -> Part:
        return self._transform(part)

    @dispatch.method
    def _transform(self, part: Part | None) -> Part:
        raise TypeError(part)

    @_transform.register
    def _transform_none(self, part: None) -> Part:
        return []

    @_transform.register
    def _transform_str(self, part: str) -> Part:
        return part

    @_transform.register
    def _transform_sequence(self, part: collections.abc.Sequence) -> Part:
        return [self(c) for c in part]

    @_transform.register
    def _transform_wrap(self, part: Wrap) -> Part:
        return Wrap(self(part.part), part.wrapper)

    @_transform.register
    def _transform_list(self, part: List) -> Part:
        return List([self(c) for c in part.parts], part.delimiter, part.trailer)

    @_transform.register
    def _transform_concat(self, part: Concat) -> Part:
        return Concat([self(c) for c in part.parts])

    @_transform.register
    def _transform_block(self, part: Block) -> Part:
        return Block([self(c) for c in part.parts])

    @_transform.register
    def _transform_section(self, part: Section) -> Part:
        return Section([self(c) for c in part.parts])

    @_transform.register
    def _transform_meta(self, part: Meta) -> Meta:
        return part


##


class RemoveMetas(PartTransform):
    @PartTransform._transform.register  # noqa
    def _transform_meta(self, part: Meta) -> Part:
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
    @PartTransform._transform.register  # noqa
    def _transform_sequence(self, part: collections.abc.Sequence) -> Part:
        return _drop_empties(self(c) for c in part)

    @PartTransform._transform.register  # noqa
    def _transform_list(self, part: List) -> Part:
        parts = _drop_empties(self(c) for c in part.parts)
        return List(parts, part.delimiter, part.trailer) if parts else []

    @PartTransform._transform.register  # noqa
    def _transform_concat(self, part: Concat) -> Part:
        parts = _drop_empties(self(c) for c in part.parts)
        return Concat(parts) if parts else []

    @PartTransform._transform.register  # noqa
    def _transform_block(self, part: Block) -> Part:
        parts = _drop_empties(self(c) for c in part.parts)
        return Block(parts) if parts else []

    @PartTransform._transform.register  # noqa
    def _transform_section(self, part: Section) -> Part:
        parts = _drop_empties(self(c) for c in part.parts)
        return Section(parts) if parts else []


compact_part = CompactPart()


##


class PartRenderer:
    def __init__(
            self,
            buf: io.StringIO,
            *,
            indent: int | str = 4,
    ) -> None:
        super().__init__()

        self._buf = buf

        self._indents = 0
        if isinstance(indent, int):
            indent = ' ' * indent
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

    def __call__(self, part: Part | None) -> None:
        return self._render(part)

    @dispatch.method
    def _render(self, part: Part | None) -> None:
        raise TypeError(part)

    @_render.register
    def _render_none(self, part: None) -> None:
        pass

    @_render.register
    def _render_str(self, part: str) -> None:
        self._write(part)

    @_render.register
    def _render_sequence(self, part: collections.abc.Sequence) -> None:
        for i, c in enumerate(part):
            if i:
                self._write(' ')
            self(c)

    @_render.register
    def _render_wrap(self, part: Wrap) -> None:
        self._write(part.wrapper[0])
        self(part.part)
        self._write(part.wrapper[1])

    @_render.register
    def _render_list(self, part: List) -> None:
        for i, c in enumerate(part.parts):
            if i:
                self._write(part.delimiter + ' ')
            self(c)
        if part.trailer:
            self._write(part.delimiter)

    @_render.register
    def _render_concat(self, part: Concat) -> None:
        for c in part.parts:
            self(c)

    @_render.register
    def _render_block(self, part: Block) -> None:
        for c in part.parts:
            self(c)
            self._write_newline()

    @_render.register
    def _render_section(self, part: Section) -> None:
        self._indents += 1
        try:
            for c in part.parts:
                self(c)
        finally:
            self._indents -= 1


def render_part(part: Part, buf: io.StringIO | None = None) -> io.StringIO:
    if buf is None:
        buf = io.StringIO()
    PartRenderer(buf)(part)
    return buf


def render(part: Part) -> str:
    part = remove_metas(part)
    part = compact_part(part)
    return render_part(part).getvalue()
