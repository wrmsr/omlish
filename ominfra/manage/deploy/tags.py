# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.check import check


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


@dc.dataclass(frozen=True)
class DeployTag(abc.ABC):  # noqa
    s: str

    def __post_init__(self) -> None:
        check.not_in(abc.ABC, type(self).__bases__)
        check.non_empty_str(self.s)
        for ch in DEPLOY_TAG_ILLEGAL_STRS:
            check.state(ch not in self.s)

    #

    tag_name: ta.ClassVar[str]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)
        if abc.ABC not in cls.__bases__:
            check.non_empty_str(tn := cls.tag_name)
            check.equal(tn, tn.lower().strip())
            check.not_in('_', tn)


##


_DEPLOY_TAGS: ta.Set[ta.Type[DeployTag]] = set()
DEPLOY_TAGS: ta.AbstractSet[ta.Type[DeployTag]] = _DEPLOY_TAGS

_DEPLOY_TAGS_BY_NAME: ta.Dict[str, ta.Type[DeployTag]] = {}
DEPLOY_TAGS_BY_NAME: ta.Mapping[str, ta.Type[DeployTag]] = _DEPLOY_TAGS_BY_NAME


def _register_deploy_tag(cls):
    check.not_in(cls.tag_name, _DEPLOY_TAGS_BY_NAME)

    _DEPLOY_TAGS.add(cls)
    _DEPLOY_TAGS_BY_NAME[cls.tag_name] = cls

    return cls


##


@_register_deploy_tag
class DeployTimestamp(DeployTag):
    tag_name: ta.ClassVar[str] = 'timestamp'


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
class DeployKeyDeployTag(KeyDeployTag):
    tag_name: ta.ClassVar[str] = 'deploy-key'


@_register_deploy_tag
class AppKeyDeployTag(KeyDeployTag):
    tag_name: ta.ClassVar[str] = 'app-key'


##


class RevDeployTag(DeployTag, abc.ABC):  # noqa
    pass


@_register_deploy_tag
class AppRevDeployTag(RevDeployTag):
    tag_name: ta.ClassVar[str] = 'app-rev'
