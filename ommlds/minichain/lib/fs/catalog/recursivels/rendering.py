"""
TODO:
 - max_depth
 - '...' marker for truncated directories
  - any directory with unlisted children will be suffixed inline with '...'
  - absence of '...' indicates an empty directory
"""
import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from .running import DirLsItem
from .running import LsItem


##


class RenderedLsLines(ta.NamedTuple):
    lines: list[str]
    joined_len: int
    is_truncated: bool


#


@dc.dataclass(eq=False)
class _LsLine:
    item: LsItem
    d: int

    _: dc.KW_ONLY

    s: str | None = None

    children: dict[str, '_LsLine'] | None = None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<{self.item.path!r}, {self.s!r}>'


@dc.dataclass()
class _LsRenderRun:
    root: DirLsItem

    _: dc.KW_ONLY

    soft_max_len: int | None = None

    @lang.cached_function
    def root_line(self) -> _LsLine:
        def rec0(cur: LsItem, *, d: int = 0) -> _LsLine:
            if isinstance(cur, DirLsItem):
                return _LsLine(
                    cur,
                    d,
                    children=({
                        child.name: rec0(child, d=d + 1)
                        for child in cur.children.values()
                    } if isinstance(cur, DirLsItem) else None),
                )

            else:
                return _LsLine(
                    cur,
                    d,
                )

        return rec0(self.root)

    @lang.cached_function
    def all_lines(self) -> ta.Sequence[_LsLine]:
        all_lines: list[_LsLine] = []

        def rec1(cur: _LsLine) -> None:
            all_lines.append(cur)
            if cur.children is not None:
                for child in cur.children.values():
                    rec1(child)

        rec1(self.root_line())
        return all_lines

    def render_item(self, item: LsItem) -> str:
        root_pfx = self.root.path + '/'

        if item.path == self.root.path:
            return f'- {self.root.path}'

        else:
            return (
                f'{"  " * (lang.strip_prefix(item.path, root_pfx).count("/") + 1)}'
                f'- {item.name}'
                f'{"/" if isinstance(item, DirLsItem) else ""}'
            )

    def collect_lines(self) -> list[str]:
        ret: list[str] = []

        def rec2(cur: _LsLine) -> None:
            if cur.s is None:
                return

            ret.append(cur.s)

            if cur.children is not None:
                for child in cur.children.values():
                    rec2(child)

        rec2(self.root_line())
        return ret

    def run(self) -> RenderedLsLines:
        cur_len = 0

        def add_line(s: str, *, force: bool = False) -> str | None:
            check.not_in('\n', s)

            nonlocal cur_len
            sl = len(s) + (1 if cur_len else 0)

            if not force and (self.soft_max_len is not None and (cur_len + sl) > self.soft_max_len):
                return None

            cur_len += sl
            return s

        #

        root_line = self.root_line()
        root_line.s = add_line(self.render_item(root_line.item), force=True)

        for root_child in check.not_none(root_line.children).values():
            root_child.s = add_line(self.render_item(root_child.item), force=True)

        sorted_lines = sorted(
            self.all_lines(),
            key=lambda line: (line.children is None, line.d),
        )

        is_truncated = False

        for cur in sorted_lines:
            if cur.s is not None:
                continue

            s = add_line(self.render_item(cur.item))
            if s is None:
                is_truncated = True
                break

            cur.s = s

        #

        return RenderedLsLines(
            self.collect_lines(),
            cur_len,
            is_truncated,
        )


#


class LsLinesRenderer:
    def __init__(
            self,
            *,
            soft_max_len: int | None = None,
    ) -> None:
        super().__init__()

        self._soft_max_len = soft_max_len

    def render(self, root: DirLsItem) -> RenderedLsLines:
        check.state(not root.path.endswith('/'))

        return _LsRenderRun(
            root,
            soft_max_len=self._soft_max_len,
        ).run()
