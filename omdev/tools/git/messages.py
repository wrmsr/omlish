import abc
import dataclasses as dc
import typing as ta

from omlish import lang


##


class GitMessageGenerator(abc.ABC):
    @abc.abstractmethod
    def generate_commit_message(self) -> str:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class TimestampGitMessageGenerator(GitMessageGenerator):
    DEFAULT_TIME_FMT: ta.ClassVar[str] = '%Y-%m-%d %H:%M:%S'
    time_fmt: str = DEFAULT_TIME_FMT

    def generate_commit_message(self) -> str:
        return lang.utcnow().strftime(self.time_fmt)


##


@dc.dataclass(frozen=True, kw_only=True)
class GitMessageGeneratorManifest:
    mod_name: str
    attr_name: str
    name: str
    aliases: ta.Collection[str] | None = None
