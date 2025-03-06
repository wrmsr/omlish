"""
TODO:
 - exclude @omlish-amalg-output files
"""
import abc
import dataclasses as dc
import os.path
import typing as ta
import urllib.request

from omdev.home.secrets import load_secrets
from omdev.tools.git.messages import GitMessageGenerator
from omlish import check
from omlish import lang
from omlish.configs.classes import Configurable
from omlish.subprocesses.sync import subprocesses

from ..minichain.backends.mlxlm import MlxlmChatModel
from ..minichain.backends.openai import OpenaiChatModel
from ..minichain.chat import UserMessage
from ..minichain.generative import MaxTokens


GitAiBackendConfigT = ta.TypeVar('GitAiBackendConfigT', bound='GitAiBackend.Config')


##


class GitAiBackend(Configurable[GitAiBackendConfigT], lang.Abstract):
    @dc.dataclass(frozen=True)
    class Config(Configurable.Config):
        max_tokens: int | None = 128

    @abc.abstractmethod
    def run_prompt(self, prompt: str) -> str:
        raise NotImplementedError


#


class OpenaiGitAiBackend(GitAiBackend['OpenaiGitAiBackend.Config']):
    @dc.dataclass(frozen=True)
    class Config(GitAiBackend.Config):
        pass

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

    def run_prompt(self, prompt: str) -> str:
        # FIXME:
        for key in ['OPENAI_API_KEY']:
            if (sec := load_secrets().try_get(key.lower())) is not None:
                os.environ[key] = sec.reveal()

        llm = OpenaiChatModel()

        resp = llm(
            [UserMessage(prompt)],
            *((MaxTokens(self._config.max_tokens),) if self._config.max_tokens is not None else ()),
        )
        return check.non_empty_str(resp.v[0].m.s)


#


class MlxlmGitAiBackend(GitAiBackend['MlxlmGitAiBackend.Config']):
    @dc.dataclass(frozen=True)
    class Config(GitAiBackend.Config):
        model: str = 'mlx-community/Qwen2.5-Coder-32B-Instruct-8bit'

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

    def run_prompt(self, prompt: str) -> str:
        llm = MlxlmChatModel(self._config.model)

        resp = llm(
            [UserMessage(prompt)],
            *((MaxTokens(self._config.max_tokens),) if self._config.max_tokens is not None else ()),
        )
        return check.non_empty_str(resp.v[0].m.s)


#


class LocalhostHttpPostGitAiBackend(GitAiBackend['LocalhostHttpPostGitAiBackend.Config']):
    @dc.dataclass(frozen=True)
    class Config(GitAiBackend.Config):
        port: int = 5067
        path: str = ''

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

    @property
    def config(self) -> Config:
        return self._config

    def run_prompt(self, prompt: str) -> str:
        with urllib.request.urlopen(urllib.request.Request(
                f'http://localhost:{self._config.port}/{self._config.path}',
                data=prompt.encode('utf-8'),
        )) as resp:
            return resp.read().decode('utf-8')


##


# @omlish-manifest omdev.tools.git.messages.GitMessageGeneratorManifest(name='ai')
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

    DEFAULT_BACKEND: ta.ClassVar[GitAiBackend] = (
        OpenaiGitAiBackend()
        # LocalhostHttpPostGitAiBackend()
    )

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
