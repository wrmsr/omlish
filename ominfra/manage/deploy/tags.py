# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.check import check
from omlish.lite.marshal import register_single_field_type_obj_marshaler


##


DEPLOY_TAG_SIGIL = '@'

DEPLOY_TAG_SEPARATOR = '--'

DEPLOY_TAG_DELIMITERS: ta.AbstractSet[str] = frozenset([
    DEPLOY_TAG_SEPARATOR,
    '.',
])

DEPLOY_TAG_ILLEGAL_STRS: ta.AbstractSet[str] = frozenset([
    DEPLOY_TAG_SIGIL,
    *DEPLOY_TAG_DELIMITERS,
    '/',
])


##


@dc.dataclass(frozen=True, order=True)
class DeployTag(abc.ABC):  # noqa
    s: str

    def __post_init__(self) -> None:
        check.not_in(abc.ABC, type(self).__bases__)
        check.non_empty_str(self.s)
        for ch in DEPLOY_TAG_ILLEGAL_STRS:
            check.state(ch not in self.s)

    #

    tag_name: ta.ClassVar[str]
    tag_kwarg: ta.ClassVar[str]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if abc.ABC in cls.__bases__:
            return

        for b in cls.__bases__:
            if issubclass(b, DeployTag):
                check.in_(abc.ABC, b.__bases__)

        check.non_empty_str(tn := cls.tag_name)
        check.equal(tn, tn.lower().strip())
        check.not_in('_', tn)

        check.state(not hasattr(cls, 'tag_kwarg'))
        cls.tag_kwarg = tn.replace('-', '_')


##


_DEPLOY_TAGS: ta.Set[ta.Type[DeployTag]] = set()
DEPLOY_TAGS: ta.AbstractSet[ta.Type[DeployTag]] = _DEPLOY_TAGS

_DEPLOY_TAGS_BY_NAME: ta.Dict[str, ta.Type[DeployTag]] = {}
DEPLOY_TAGS_BY_NAME: ta.Mapping[str, ta.Type[DeployTag]] = _DEPLOY_TAGS_BY_NAME

_DEPLOY_TAGS_BY_KWARG: ta.Dict[str, ta.Type[DeployTag]] = {}
DEPLOY_TAGS_BY_KWARG: ta.Mapping[str, ta.Type[DeployTag]] = _DEPLOY_TAGS_BY_KWARG


def _register_deploy_tag(cls):
    check.not_in(cls.tag_name, _DEPLOY_TAGS_BY_NAME)
    check.not_in(cls.tag_kwarg, _DEPLOY_TAGS_BY_KWARG)

    _DEPLOY_TAGS.add(cls)
    _DEPLOY_TAGS_BY_NAME[cls.tag_name] = cls
    _DEPLOY_TAGS_BY_KWARG[cls.tag_kwarg] = cls

    register_single_field_type_obj_marshaler('s', cls)

    return cls


##


@_register_deploy_tag
class DeployTime(DeployTag):
    tag_name: ta.ClassVar[str] = 'time'


##


class NameDeployTag(DeployTag, abc.ABC):  # noqa
    pass


@_register_deploy_tag
class DeployApp(NameDeployTag):
    tag_name: ta.ClassVar[str] = 'app'


@_register_deploy_tag
class DeployConf(NameDeployTag):
    tag_name: ta.ClassVar[str] = 'conf'


##


class KeyDeployTag(DeployTag, abc.ABC):  # noqa
    pass


@_register_deploy_tag
class DeployKey(KeyDeployTag):
    tag_name: ta.ClassVar[str] = 'deploy-key'


@_register_deploy_tag
class DeployAppKey(KeyDeployTag):
    tag_name: ta.ClassVar[str] = 'app-key'


##


class RevDeployTag(DeployTag, abc.ABC):  # noqa
    pass


@_register_deploy_tag
class DeployAppRev(RevDeployTag):
    tag_name: ta.ClassVar[str] = 'app-rev'


##


class DeployTagMap:
    def __init__(
            self,
            *args: DeployTag,
            **kwargs: str,
    ) -> None:
        super().__init__()

        dct: ta.Dict[ta.Type[DeployTag], DeployTag] = {}

        for a in args:
            c = type(check.isinstance(a, DeployTag))
            check.not_in(c, dct)
            dct[c] = a

        for k, v in kwargs.items():
            c = DEPLOY_TAGS_BY_KWARG[k]
            check.not_in(c, dct)
            dct[c] = c(v)

        self._dct = dct
        self._tup = tuple(sorted((type(t).tag_kwarg, t.s) for t in dct.values()))

    #

    def add(self, *args: ta.Any, **kwargs: ta.Any) -> 'DeployTagMap':
        return DeployTagMap(
            *self,
            *args,
            **kwargs,
        )

    def remove(self, *tags_or_names: ta.Union[ta.Type[DeployTag], str]) -> 'DeployTagMap':
        dcs = {
            check.issubclass(a, DeployTag) if isinstance(a, type) else DEPLOY_TAGS_BY_NAME[a]
            for a in tags_or_names
        }

        return DeployTagMap(*[
            t
            for t in self._dct.values()
            if t not in dcs
        ])

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(f"{k}={v!r}" for k, v in self._tup)})'

    def __hash__(self) -> int:
        return hash(self._tup)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DeployTagMap):
            return self._tup == other._tup
        else:
            return NotImplemented

    #

    def __len__(self) -> int:
        return len(self._dct)

    def __iter__(self) -> ta.Iterator[DeployTag]:
        return iter(self._dct.values())

    def __getitem__(self, key: ta.Union[ta.Type[DeployTag], str]) -> DeployTag:
        if isinstance(key, str):
            return self._dct[DEPLOY_TAGS_BY_NAME[key]]
        elif isinstance(key, type):
            return self._dct[key]
        else:
            raise TypeError(key)

    def __contains__(self, key: ta.Union[ta.Type[DeployTag], str]) -> bool:
        if isinstance(key, str):
            return DEPLOY_TAGS_BY_NAME[key] in self._dct
        elif isinstance(key, type):
            return key in self._dct
        else:
            raise TypeError(key)
