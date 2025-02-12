# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.lite.check import check


HierarchyTagStringValue = ta.Tuple[str, ...]  # ta.TypeAlias
TagStringValue = ta.Union[bool, str, HierarchyTagStringValue]  # ta.TypeAlias
TagStringValueT = ta.TypeVar('TagStringValueT', bound=TagStringValue)


##


TAG_STRING_VALUE_TYPES: ta.Tuple = (
    bool,
    str,
    HierarchyTagStringValue,
)


TAG_STRING_BOOL_STR_MAP: ta.Mapping[str, bool] = {
    'true': True,
    'false': False,
}


def check_tag_string_string(s: str) -> str:
    check.non_empty_str(s)
    check.equal(s.lower().strip(), s)
    check.not_in(':', s)
    return s


def build_hierarchy_tag_string_values(
        m: ta.Mapping[str, ta.Any],
) -> ta.FrozenSet[HierarchyTagStringValue]:
    def rec(c):
        if isinstance(c, str):
            yield (c,)
        elif isinstance(c, ta.Mapping):
            for k, v in c.items():
                yield (k,)
                for n in rec(v):
                    yield (k, *n)
        else:
            raise TypeError(c)

    return frozenset(rec(m))


##


@dc.dataclass(frozen=True)
class TagString(ta.Generic[TagStringValueT]):
    name: str
    type: ta.Type[TagStringValueT]

    valid_values: ta.Optional[ta.FrozenSet[TagStringValueT]] = None
    set: bool = False

    def __post_init__(self) -> None:
        check_tag_string_string(self.name)

        check.in_(self.type, TAG_STRING_VALUE_TYPES)

        if self.valid_values is not None:
            check.isinstance(self.valid_values, frozenset)

            v: ta.Any
            if self.type is bool:
                for v in self.valid_values:
                    check.isinstance(v, bool)

            elif self.type is str:
                for v in self.valid_values:
                    check_tag_string_string(v)

            elif self.type is HierarchyTagStringValue:
                for v in self.valid_values:
                    check.isinstance(v, tuple)
                    for c in v:
                        check_tag_string_string(c)
                    for i in range(1, len(v)):
                        p = v[:-i]
                        check.in_(p, self.valid_values)

            else:
                raise TypeError(self.type)

    #

    @classmethod
    def new_bool(
            cls,
            name: str,
            valid_values: ta.Optional[ta.Iterable[bool]] = None,
            **kwargs: ta.Any,
    ) -> 'TagString':
        return cls(
            name=name,
            type=bool,  # type: ignore
            valid_values=(
                frozenset(valid_values)  # type: ignore
                if valid_values is not None else None
            ),
            **kwargs,
        )

    @classmethod
    def new_str(
            cls,
            name: str,
            valid_values: ta.Optional[ta.Iterable[str]] = None,
            **kwargs: ta.Any,
    ) -> 'TagString':
        return cls(
            name=name,
            type=str,  # type: ignore
            valid_values=(
                frozenset(check.not_isinstance(valid_values, str))  # type: ignore
                if valid_values is not None else None
            ),
            **kwargs,
        )

    @classmethod
    def new_hierarchy(
            cls,
            name: str,
            valid_values: ta.Optional[ta.Mapping[str, ta.Any]] = None,
            **kwargs: ta.Any,
    ) -> 'TagString':
        return cls(
            name=name,
            type=HierarchyTagStringValue,  # type: ignore
            valid_values=(
                build_hierarchy_tag_string_values(valid_values)  # type: ignore
                if valid_values is not None else None
            ),
            **kwargs,
        )


@dc.dataclass(frozen=True)
class TagStringSet:
    dct: ta.Mapping[str, ta.FrozenSet[TagStringValue]]


##


class TagStringCatalog:
    def __init__(self, tags: ta.Iterable[TagString]) -> None:
        super().__init__()

        dct: ta.Dict[str, TagString] = {}
        for t in tags:
            check.not_in(t.name, dct)
            dct[t.name] = t
        self._by_name = dct

    class Parsed(ta.NamedTuple):
        tag: TagString
        values: ta.FrozenSet[TagStringValue]

    def parse_one(self, s: str) -> Parsed:
        name, *rest = check.non_empty_str(s).split(':')

        tag = self._by_name[name]

        #

        v: TagStringValue
        if tag.type is bool:
            bs = check.single(rest)
            v = TAG_STRING_BOOL_STR_MAP[bs]

        elif tag.type is str:
            v = check.single(rest)

        elif tag.type is HierarchyTagStringValue:
            v = tuple(rest)

        else:
            raise TypeError(tag.type)

        #

        if tag.valid_values is not None:
            check.in_(v, tag.valid_values)

        #

        vs: ta.FrozenSet[TagStringValue]
        if tag.type is HierarchyTagStringValue:
            vt = check.isinstance(v, tuple)
            vs = frozenset(vt[:i + 1] for i in range(len(vt)))
        else:
            vs = frozenset([v])

        #

        return TagStringCatalog.Parsed(tag, vs)

    def parse_set(self, *strs: str) -> TagStringSet:
        dct: ta.Dict[str, ta.Set[TagStringValue]] = {}

        for s in strs:
            p = self.parse_one(s)

            if not p.tag.set:
                check.not_in(p.tag.name, dct)

            dct.setdefault(p.tag.name, set()).update(p.values)

        return TagStringSet({k: frozenset(v) for k, v in dct.items()})
