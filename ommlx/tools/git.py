import abc
import dataclasses as dc
import os.path
import typing as ta

from omdev.home.paths import get_home_dir
from omdev.tools.git.messages import GitMessageGenerator
from omdev.tools.git.messages import GitMessageGeneratorManifest
from omlish import check
from omlish.formats import dotenv
from omlish.subprocesses.sync import subprocesses

from ..minichain.backends.openai import OpenaiChatModel
from ..minichain.chat import UserMessage
from ..minichain.generative import MaxTokens


##


class GitAiBackend(abc.ABC):
    @dc.dataclass(frozen=True)
    class Config:
        max_tokens: int | None = 128

    def __init__(self, config: Config = Config()) -> None:
        super().__init__()

        self._config = config

    @abc.abstractmethod
    def run_prompt(self, prompt: str) -> str:
        raise NotImplementedError


#


class OpenaiGitAiBackend(GitAiBackend):
    def run_prompt(self, prompt: str) -> str:
        with open(os.path.join(get_home_dir(), 'llm/.env')) as f:
            dotenv.Dotenv(stream=f).apply_to(os.environ)

        llm = OpenaiChatModel()

        resp = llm(
            [UserMessage(prompt)],
            *((MaxTokens(self._config.max_tokens),) if self._config.max_tokens is not None else ()),
        )
        return check.non_empty_str(resp.v[0].m.s)


##


class AiGitMessageGenerator(GitMessageGenerator):
    def __init__(
            self,
            *,
            backend: GitAiBackend | None = None,
    ) -> None:
        super().__init__()

        if backend is None:
            backend = self.DEFAULT_BACKEND
        self._backend = backend

    DEFAULT_BACKEND: ta.ClassVar[GitAiBackend] = OpenaiGitAiBackend()

    def generate_commit_message(
            self,
            args: GitMessageGenerator.GenerateCommitMessageArgs,
    ) -> GitMessageGenerator.GenerateCommitMessageResult:
        diff = subprocesses.check_output(
            'git',
            'diff',
            'HEAD',
            '--',
            ':(exclude)**/.manifests.json',  # TODO: configurable
            cwd=args.cwd,
        ).decode()

        prompt = '\n\n'.join([
            'Write a short git commit message for the following git diff:',
            f'```\n{diff}\n```',
        ])

        msg = self._backend.run_prompt(prompt)

        return GitMessageGenerator.GenerateCommitMessageResult(
            msg=msg,
            confirm=True,
        )


#


# @omlish-manifest
_AI_GIT_MESSAGE_GENERATOR_MANIFEST = GitMessageGeneratorManifest(
    mod_name=__name__,
    attr_name='AiGitMessageGenerator',
    name='ai',
)
