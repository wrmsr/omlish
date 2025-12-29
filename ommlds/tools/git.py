"""
TODO:
 - move omit magic to omdev lol
"""
import abc
import dataclasses as dc
import re
import typing as ta
import urllib.request

from omdev.git.magic import GIT_DIFF_OMIT_MAGIC_COMMENT
from omdev.py.srcheaders import get_py_header_lines
from omdev.tools.git.messages import GitMessageGenerator
from omlish import check
from omlish import lang
from omlish.configs.classes import Configurable
from omlish.http import all as http
from omlish.subprocesses.sync import subprocesses

from .. import minichain as mc
from ..cli.secrets import install_env_secrets
from ..server.client import McServerClient


GitAiBackendConfigT = ta.TypeVar('GitAiBackendConfigT', bound='GitAiBackend.Config')


##


class GitAiBackend(Configurable[GitAiBackendConfigT], lang.Abstract):
    @dc.dataclass(frozen=True, kw_only=True)
    class Config(Configurable.Config):
        max_tokens: int | None = 128

    @abc.abstractmethod
    def run_prompt(self, prompt: str) -> str:
        raise NotImplementedError


def _get_single_ai_message_str(resp: mc.ChatChoicesResponse) -> str:
    return check.not_empty(
        check.isinstance(
            check.isinstance(
                check.single(
                    check.single(
                        resp.v,
                    ).ms,
                ),
                mc.AiMessage,
            ).c,
            str,
        ),
    )


#


class StandardGitAiBackend(GitAiBackend['StandardGitAiBackend.Config']):
    @dc.dataclass(frozen=True, kw_only=True)
    class Config(GitAiBackend.Config):
        backend: str | None = None

    DEFAULT_BACKEND_NAME: str = 'openai'

    def __init__(
            self,
            config: Config = Config(),
            *,
            backend_catalog: ta.Optional['mc.BackendCatalog'] = None,
    ) -> None:
        super().__init__(config)

        if backend_catalog is None:
            backend_catalog = mc.BackendStringBackendCatalog()
        self._backend_catalog = backend_catalog

    def run_prompt(self, prompt: str) -> str:
        install_env_secrets()  # FIXME

        be = self._backend_catalog.get_backend(
            mc.ChatChoicesService,  # type: ignore[type-abstract]
            self._config.backend or self.DEFAULT_BACKEND_NAME,
        )

        llm = be.factory(
            http_client=http.SyncAsyncHttpClient(http.client()),  # FIXME
        )

        resp = lang.sync_await(llm.invoke(mc.ChatChoicesRequest(
            [mc.UserMessage(prompt)],
            # FIXME:  *((MaxTokens(self._config.max_tokens),) if self._config.max_tokens is not None else ()),
        )))
        return _get_single_ai_message_str(resp)


#


def _strip_markdown_code_block(text: str) -> str:
    if (match := re.fullmatch(r'```(?:\w+)?\n(.+?)\n```', text, re.DOTALL)) is None:
        return text
    return match.group(1)


# class MlxGitAiBackend(GitAiBackend['MlxGitAiBackend.Config']):
#     @dc.dataclass(frozen=True, kw_only=True)
#     class Config(GitAiBackend.Config):
#         model: str = 'mlx-community/Qwen2.5-Coder-32B-Instruct-8bit'
#
#         run_in_subprocess: bool = True
#         subprocess_timeout: float | None = 60.
#
#     def __init__(self, config: Config = Config()) -> None:
#         super().__init__(config)
#
#     def _run_prompt(self, prompt: str) -> str:
#         with mc_mlx_chat.MlxChatChoicesService(mc.ModelRepo.parse(self._config.model)) as llm:
#             resp = lang.sync_await(llm.invoke(mc.ChatChoicesRequest(
#                 [mc.UserMessage(prompt)],
#                 # FIXME: *((MaxTokens(self._config.max_tokens),) if self._config.max_tokens is not None else ()),
#             )))
#             text = _get_single_ai_message_str(resp)
#
#             text = _strip_markdown_code_block(text)
#
#             return text
#
#     def run_prompt(self, prompt: str) -> str:
#         if self._config.run_in_subprocess:
#             # tokenizers installs a pthread_atfork callback at *import* time:
#             #   https://github.com/huggingface/tokenizers/blob/4f1a810aa258d287e6936315e63fbf58bde2a980/bindings/python/src/lib.rs#L57  # noqa
#             # then complains about `TOKENIZERS_PARALLELISM` at the next fork (which presumably will happen immediately
#             # after this to `git commit`, despite it being conceptually just a fork/exe).
#             # TODO: a generic subprocessing minichain service wrapper?
#             with cf.ProcessPoolExecutor() as exe:
#                 return exe.submit(
#                     self._run_prompt,
#                     prompt,
#                 ).result(timeout=self._config.subprocess_timeout)
#
#         else:
#             return self._run_prompt(prompt)


#


class LocalhostHttpPostGitAiBackend(GitAiBackend['LocalhostHttpPostGitAiBackend.Config']):
    @dc.dataclass(frozen=True, kw_only=True)
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
    @dc.dataclass(frozen=True, kw_only=True)
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
            backend: GitAiBackend | str | None = None,
    ) -> None:
        super().__init__()

        if backend is None:
            backend = self.DEFAULT_BACKEND
        elif isinstance(backend, str):
            backend = StandardGitAiBackend(
                config=StandardGitAiBackend.Config(
                    backend=backend,
                ),
            )
        self._backend = check.isinstance(backend, GitAiBackend)

    DEFAULT_BACKEND: ta.ClassVar[GitAiBackend] = (
        StandardGitAiBackend()
        # LocalhostHttpPostGitAiBackend()
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

        hls = get_py_header_lines(f_src)

        return any(
            hl.src.strip() in (
                '# @omlish-generated',
                GIT_DIFF_OMIT_MAGIC_COMMENT,
            )
            for hl in hls
        )

    # TODO: configurable
    DEFAULT_EXCLUDES: ta.ClassVar[ta.Sequence[str]] = [
        '**/.omlish-manifests.json',
        '**/_antlr/*',
    ]

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
            *[f':(exclude){x}' for x in [*self.DEFAULT_EXCLUDES, *excludes]],
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
                '- Output only the commit message, with no additional text.',
                '- Output plain text, not markdown. Do not begin your response with "```".',
            ]),
        ])

        msg = self._backend.run_prompt(prompt)

        return GitMessageGenerator.GenerateCommitMessageResult(
            msg=msg,
            confirm=True,
        )
