"""
TODO:
 - move omit magic to omdev lol
"""
import abc
import concurrent.futures as cf
import dataclasses as dc
import os.path
import re
import typing as ta
import urllib.request

from omdev.git.magic import GIT_DIFF_OMIT_MAGIC_COMMENT
from omdev.home.secrets import load_secrets
from omdev.tools.git.messages import GitMessageGenerator
from omlish import check
from omlish import lang
from omlish.configs.classes import Configurable
from omlish.subprocesses.sync import subprocesses

from .. import minichain as mc
from ..minichain.backends.mlxlm import MlxlmChatModel
from ..minichain.backends.openai import OpenaiChatModel
from ..minichain.generative import MaxTokens
from ..server.client import McServerClient


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
            [mc.UserMessage(prompt)],
            *((MaxTokens(self._config.max_tokens),) if self._config.max_tokens is not None else ()),
        )
        return check.non_empty_str(resp.v[0].m.s)


#


def _strip_markdown_code_block(text: str) -> str:
    if (match := re.fullmatch(r'```(?:\w+)?\n(.+?)\n```', text, re.DOTALL)) is None:
        return text
    return match.group(1)


class MlxlmGitAiBackend(GitAiBackend['MlxlmGitAiBackend.Config']):
    @dc.dataclass(frozen=True)
    class Config(GitAiBackend.Config):
        model: str = 'mlx-community/Qwen2.5-Coder-32B-Instruct-8bit'

        run_in_subprocess: bool = True
        subprocess_timeout: float | None = 60.

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

    def _run_prompt(self, prompt: str) -> str:
        llm = MlxlmChatModel(self._config.model)

        resp = llm(
            [mc.UserMessage(prompt)],
            *((MaxTokens(self._config.max_tokens),) if self._config.max_tokens is not None else ()),
        )
        text = check.non_empty_str(resp.v[0].m.s)

        text = _strip_markdown_code_block(text)

        return text

    def run_prompt(self, prompt: str) -> str:
        if self._config.run_in_subprocess:
            # tokenizers installs a pthread_atfork callback at *import* time:
            #   https://github.com/huggingface/tokenizers/blob/4f1a810aa258d287e6936315e63fbf58bde2a980/bindings/python/src/lib.rs#L57
            # then complains about `TOKENIZERS_PARALLELISM` at the next fork (which presumably will happen immediately
            # after this to `git commit`, despite it being conceptually just a fork/exe).
            # TODO: a generic subprocessing minichain service wrapper?
            with cf.ProcessPoolExecutor() as exe:
                return exe.submit(
                    self._run_prompt,
                    prompt,
                ).result(timeout=self._config.subprocess_timeout)

        else:
            return self._run_prompt(prompt)


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


#


class McServerGitAiBackend(GitAiBackend['McServerGitAiBackend.Config']):
    @dc.dataclass(frozen=True)
    class Config(GitAiBackend.Config):
        pass

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

    def run_prompt(self, prompt: str) -> str:
        text = McServerClient().prompt(
            prompt,
            launch=True,
        )

        text = _strip_markdown_code_block(text)

        return text


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
        # MlxlmGitAiBackend()
        # McServerGitAiBackend()
    )

    def _should_exclude_file_name(self, fn: str) -> bool:
        if not fn.endswith('.py'):
            return False

        try:
            with open(fn) as f:
                f_src = f.read()
        except FileNotFoundError:
            return False

        return any(
            l.startswith(GIT_DIFF_OMIT_MAGIC_COMMENT)
            for l in f_src.splitlines()
        )

    def generate_commit_message(
            self,
            args: GitMessageGenerator.GenerateCommitMessageArgs,
    ) -> GitMessageGenerator.GenerateCommitMessageResult:
        diff_files = subprocesses.check_output(
            'git',
            'diff',
            '--name-only',
            'HEAD',
        ).decode().splitlines()

        excludes = [
            fn
            for fn in diff_files
            if self._should_exclude_file_name(fn)
        ]

        diff = subprocesses.check_output(
            'git',
            'diff',
            'HEAD',
            '--',
            ':(exclude)**/.manifests.json',  # TODO: configurable
            *[f':(exclude){x}' for x in excludes],
            cwd=args.cwd,
        ).decode()

        prompt = '\n\n'.join([
            'Write a short git commit message for the following git diff:',
            f'```\n{diff}\n```',
            '\n'.join([
                'Follow these rules:',
                '- Use imperative tense (e.g., "Fix bug", "Add feature").',
                '- Be concise but descriptive. Avoid vague messages like "Update X".',
                '- Do not mention files explicitly unless necessary.',
                '- If the change is complex, add a second paragraph with more details.',
                'Output only the commit message, with no additional text.',
            ]),
        ])

        msg = self._backend.run_prompt(prompt)

        return GitMessageGenerator.GenerateCommitMessageResult(
            msg=msg,
            confirm=True,
        )
