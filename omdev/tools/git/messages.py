import abc
import dataclasses as dc
import os
import typing as ta

from omlish import cached
from omlish import check
from omlish import lang
from omlish.manifests import load as manifest_load
from omlish.manifests.base import ModAttrManifest


##


class GitMessageGenerator(abc.ABC):
    @dc.dataclass(frozen=True, kw_only=True)
    class GenerateCommitMessageArgs:
        cwd: str | None = None

        DEFAULT_TIME_FMT: ta.ClassVar[str] = '%Y-%m-%dT%H:%M:%SZ'
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
class GitMessageGeneratorManifest(ModAttrManifest):
    name: str
    aliases: ta.Collection[str] | None = None

    def load_cls(self) -> type[GitMessageGenerator]:
        return check.issubclass(self.load(), GitMessageGenerator)


@cached.function
def load_message_generator_manifests() -> ta.Sequence[GitMessageGeneratorManifest]:
    ldr = manifest_load.MANIFEST_LOADER
    pkgs = ldr.scan_or_discover_pkgs(fallback_root=os.getcwd())
    mfs = ldr.load(*pkgs, only=[GitMessageGeneratorManifest])
    return [mf.value for mf in mfs]


@cached.function
def load_message_generator_manifests_map() -> ta.Mapping[str, GitMessageGeneratorManifest]:
    dct: dict[str, GitMessageGeneratorManifest] = {}
    for m in load_message_generator_manifests():
        for n in (m.name, *(m.aliases or ())):
            check.not_in(n, dct)
            dct[n] = m
    return dct


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
_TIMESTAMP_GIT_MESSAGE_GENERATOR_MANIFEST = GitMessageGeneratorManifest(
    mod_name=__name__,
    attr_name='TimestampGitMessageGenerator',
    name='timestamp',
    aliases=['ts'],
)
