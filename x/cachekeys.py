# ruff: noqa: UP006 UP007
import dataclasses as dc
import itertools
import typing as ta

from omlish.lite.check import check


CacheKeyPart = ta.Union[str, 'CacheKey']  # ta.TypeAlias


##


@dc.dataclass(frozen=True)
class CacheKey:
    level: int
    parts: ta.Tuple[CacheKeyPart, ...]

    #

    @classmethod
    def of(cls, *objs: ta.Any) -> 'CacheKey':
        if len(objs) == 1 and isinstance(obj := objs[0], CacheKey):
            return obj

        def prepare(o):
            if isinstance(o, CacheKey):
                return o.level, o
            elif isinstance(o, str):
                return 0, o
            elif isinstance(o, ta.Sequence):
                max_lvl = 0
                out_lst = []
                for c in o:
                    cur_lvl, cur_out = prepare(c)
                    max_lvl = max(max_lvl, cur_lvl)
                    if out_lst and all(
                            isinstance(x, ta.Sequence) and not isinstance(x, str)
                            for x in (out_lst[-1], cur_out)
                    ):
                        out_lst[-1].extend(cur_out)
                    else:
                        out_lst.append(cur_out)
                if len(out_lst) == 1 and isinstance(out_lst[0], ta.Sequence) and not isinstance(out_lst[0], str):
                    return max_lvl + 1, out_lst[0]
                else:
                    return max_lvl + 1, out_lst
            else:
                raise TypeError(o)
        level, objs = prepare(objs)

        def build(l, os):
            if isinstance(os, CacheKey):
                check.state(l == os.level)
                return os
            elif isinstance(os, str):
                raise TypeError(os)
            pl = []
            for ck, cg in itertools.groupby(os, key=lambda o: isinstance(o, str)):
                if ck:
                    pl.extend(cg)
                else:
                    for c in cg:
                        pl.append(build(l - 1, c))
            return CacheKey(l, tuple(pl))
        return build(level, objs)

    #

    @property
    def total_parts(self) -> int:
        return sum(p.total_parts if isinstance(p, CacheKey) else 1 for p in self.parts)

    def all_parts(self) -> ta.Iterator[CacheKeyPart]:
        for p in self.parts:
            if isinstance(p, CacheKey):
                yield p
                yield from p.all_parts()
            elif isinstance(p, str):
                yield p
            else:
                raise TypeError(p)

    #

    @property
    def head(self) -> str:
        if isinstance(p := self.parts[0], CacheKey):
            return p.head
        else:
            return check.isinstance(p, str)

    @property
    def tail(self) -> str:
        if isinstance(p := self.parts[-1], CacheKey):
            return p.tail
        else:
            return check.isinstance(p, str)

    #

    def __post_init__(self) -> None:
        check.arg(self.level > 0)
        check.arg(len(self.parts))

        check.isinstance(self.parts, tuple)
        head_str: ta.Optional[str] = None
        last_str: ta.Optional[str] = None
        num_parts = 0
        for p in self.all_parts():
            num_parts += 1
            if isinstance(p, CacheKey):
                check.arg(p.level < self.level)
            else:
                s = check.isinstance(p, str)
                if head_str is None:
                    head_str = s
                else:
                    if last_str is not None:
                        check.non_empty_str(last_str)
                    last_str = s
        if num_parts == 2:
            check.arg(check.not_none(head_str) or check.not_none(last_str))

    #

    def prepend(self, *parts: CacheKeyPart) -> 'CacheKey':
        return dc.replace(self, parts=(*parts, *self.parts))

    def append(self, *parts: CacheKeyPart) -> 'CacheKey':
        return dc.replace(self, parts=(*self.parts, *parts))

    #

    DEFAULT_SEPARATOR: ta.ClassVar[str] = '-'

    def render(self, separator: ta.Optional[str] = None) -> str:
        if separator is None:
            separator = self.DEFAULT_SEPARATOR

        lst = []
        for p in self.parts:
            if isinstance(p, CacheKey):
                lst.append(p.render(separator))
            elif isinstance(p, str):
                check.not_in(separator, p)
                lst.append(p)
            else:
                raise TypeError(p)

        return (separator * self.level).join(lst)


##


def _main() -> None:
    assert CacheKey.of(['a'], ['b']) == CacheKey(2, ('a', 'b'))

    assert CacheKey(1, ('foo',)).render() == 'foo'
    assert CacheKey(1, ('foo', 'bar')).render() == 'foo-bar'

    assert CacheKey(2, ('foo',)).render() == 'foo'
    assert CacheKey(2, ('foo', 'bar')).render() == 'foo--bar'
    assert CacheKey(2, ('foo', CacheKey(1, ('bar',)), 'baz')).render() == 'foo--bar--baz'
    assert CacheKey(2, ('foo', CacheKey(1, ('bar', 'baz')), 'qux')).render() == 'foo--bar-baz--qux'
    assert CacheKey(2, ('foo', CacheKey(1, ('bar', 'baz')), 'qux', CacheKey(1, ('barf1', 'barf2')), 'barf3')).render() == \
        'foo--bar-baz--qux--barf1-barf2--barf3'

    assert CacheKey(1, ('',)).render() == ''
    assert CacheKey(1, ('', 'a')).render() == '-a'
    assert CacheKey(1, ('a', '')).render() == 'a-'
    assert CacheKey(2, ('a', CacheKey(1, ('b',)), '')).render() == 'a--b--'
    assert CacheKey(2, ('', CacheKey(1, ('a', 'b')))).render() == '--a-b'
    assert CacheKey(2, ('', CacheKey(1, ('a',)), 'b')).render() == '--a--b'
    assert CacheKey(2, ('a', CacheKey(1, ('b', 'c')), '')).render() == 'a--b-c--'
    assert CacheKey(2, ('', CacheKey(1, ('a', 'b')), 'c')).render() == '--a-b--c'

    assert CacheKey(2, ('', CacheKey(1, ('b', '')))).render() == '--b-'
    assert CacheKey(2, ('', CacheKey(1, ('b',)), '')).render() == '--b--'

    for ckf in [
        lambda: CacheKey(1, ('', '')),
        lambda: CacheKey(2, ('', CacheKey(1, ('', 'b')))),
        lambda: CacheKey(1, ('-',)),
    ]:
        try:
            print(ckf().render())
        except Exception:  # noqa
            pass
        else:
            raise Exception

    assert CacheKey.of('') == CacheKey(1, ('',))
    assert CacheKey.of(CacheKey(1, ('a',))) == CacheKey(1, ('a',))
    assert CacheKey.of('a') == CacheKey(1, ('a',))
    assert CacheKey.of('a', 'b') == CacheKey(1, ('a', 'b'))
    assert CacheKey.of(['a']) == CacheKey(2, ('a',))
    assert CacheKey.of(['a', 'b']) == CacheKey(2, ('a', 'b'))
    assert CacheKey.of(['a'], ['b']) == CacheKey(2, ('a', 'b'))
    assert CacheKey.of(['a'], 'b') == CacheKey(2, (CacheKey(1, ('a',)), 'b'))
    assert CacheKey.of('a', ['b']) == CacheKey(2, ('a', CacheKey(1, ('b',))))
    assert CacheKey.of('a', CacheKey(2, ('b',))) == CacheKey(3, ('a', CacheKey(2, ('b',))))
    assert CacheKey.of('a', [CacheKey(2, ('b',))]) == CacheKey(4, ('a', CacheKey(3, (CacheKey(2, ('b',)),))))


if __name__ == '__main__':
    _main()
