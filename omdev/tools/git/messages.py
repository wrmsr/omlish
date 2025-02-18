import abc
import os
import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish.manifests import load as manifest_load
from omlish.manifests.base import ModAttrManifest
from omlish.manifests.base import NameAliasesManifest
from omlish.manifests.static import StaticModAttrManifest

from . import consts


##


class GitMessageGenerator(abc.ABC):
    @dc.dataclass(frozen=True, kw_only=True)
    class GenerateCommitMessageArgs:
        cwd: str | None = None

        DEFAULT_TIME_FMT: ta.ClassVar[str] = consts.DEFAULT_TIME_FMT
        time_fmt: str = DEFAULT_TIME_FMT

    @dc.dataclass(frozen=True, kw_only=True)
    class GenerateCommitMessageResult:
        msg: str

        confirm: bool = False

    @abc.abstractmethod
    def generate_commit_message(self, args: GenerateCommitMessageArgs) -> GenerateCommitMessageResult:
        raise NotImplementedError


#


@dc.dataclass(frozen=True, kw_only=True)
class GitMessageGeneratorManifest(NameAliasesManifest, ModAttrManifest):
    def load_cls(self) -> type[GitMessageGenerator]:
        return check.issubclass(self.load(), GitMessageGenerator)


class StaticGitMessageGeneratorManifest(StaticModAttrManifest, GitMessageGeneratorManifest, abc.ABC):
    pass


#


@cached.function
def load_message_generator_manifests() -> ta.Sequence[GitMessageGeneratorManifest]:
    ldr = manifest_load.MANIFEST_LOADER
    pkgs = ldr.scan_or_discover_pkgs(fallback_root=os.getcwd())
    mfs = ldr.load(*pkgs, only=[GitMessageGeneratorManifest])
    return [mf.value for mf in mfs]


@cached.function
def load_message_generator_manifests_map() -> ta.Mapping[str, GitMessageGeneratorManifest]:
    return GitMessageGeneratorManifest.build_name_dict(load_message_generator_manifests())


##


@dc.dataclass(frozen=True)
class TimestampGitMessageGenerator(GitMessageGenerator):
    def generate_commit_message(
            self,
            args: GitMessageGenerator.GenerateCommitMessageArgs,
    ) -> GitMessageGenerator.GenerateCommitMessageResult:
        return GitMessageGenerator.GenerateCommitMessageResult(
            msg=lang.utcnow().strftime(args.time_fmt),
        )


#


# @omlish-manifest
class _TIMESTAMP_GIT_MESSAGE_GENERATOR_MANIFEST(StaticGitMessageGeneratorManifest):  # noqa
    attr_name = 'TimestampGitMessageGenerator'
    name = 'timestamp'
    aliases = ['ts']  # noqa
