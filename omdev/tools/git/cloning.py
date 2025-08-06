import abc
import dataclasses as dc
import re

from omlish import lang


##


@dc.dataclass(frozen=True)
class CloneTarget(lang.Abstract, lang.Sealed):
    @abc.abstractmethod
    def render(self) -> str:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class GithubCloneTarget(CloneTarget, lang.Final):
    user: str
    repo: str

    def render(self) -> str:
        return f'git@github.com:{self.user}/{self.repo}.git'


@dc.dataclass(frozen=True)
class OtherCloneTarget(CloneTarget, lang.Final):
    s: str

    def render(self) -> str:
        return self.s


_GITHUB_PAT = re.compile(r'((http(s)?://)?(www\./)?github(\.com)?/)?(?P<user>[^/.]+)/(?P<repo>[^/.]+)(/.*)?')


def parse_clone_target(s: str) -> CloneTarget:
    if (m := _GITHUB_PAT.fullmatch(s)):
        return GithubCloneTarget(m.group('user'), m.group('repo'))
    else:
        return OtherCloneTarget(s)
