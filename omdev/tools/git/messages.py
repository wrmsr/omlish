import abc
import dataclasses as dc
import os
import typing as ta

from omlish import cached
from omlish import lang
from omlish.manifests import load as manifest_load


##


class GitMessageGenerator(abc.ABC):
    @abc.abstractmethod
    def generate_commit_message(self) -> str:
        raise NotImplementedError


#


@dc.dataclass(frozen=True, kw_only=True)
class GitMessageGeneratorManifest:
    mod_name: str
    attr_name: str
    name: str
    aliases: ta.Collection[str] | None = None


@cached.function
def load_message_generator_manifests() -> ta.Sequence[GitMessageGeneratorManifest]:
    ldr = manifest_load.MANIFEST_LOADER
    pkgs = ldr.scan_or_discover_pkgs(fallback_root=os.getcwd())
    mfs = ldr.load(*pkgs, only=[GitMessageGeneratorManifest])
    return [mf.value for mf in mfs]


##


@dc.dataclass(frozen=True)
class TimestampGitMessageGenerator(GitMessageGenerator):
    DEFAULT_TIME_FMT: ta.ClassVar[str] = '%Y-%m-%d %H:%M:%S'
    time_fmt: str = DEFAULT_TIME_FMT

    def generate_commit_message(self) -> str:
        return lang.utcnow().strftime(self.time_fmt)


#


# @omlish-manifest
_TIMESTAMP_GIT_MESSAGE_GENERATOR_MANIFEST = GitMessageGeneratorManifest(
    mod_name=__name__,
    attr_name='TimestampGitMessageGenerator',
    name='timestamp',
    aliases=['ts'],
)
