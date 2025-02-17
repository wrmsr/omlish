import dataclasses as dc
import os.path

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


class AiGitMessageGenerator(GitMessageGenerator):
    @dc.dataclass(frozen=True)
    class Config:
        max_tokens: int | None = 128

    def __init__(self, config: Config = Config()) -> None:
        super().__init__()

        self._config = config

    def generate_commit_message(
            self,
            args: GitMessageGenerator.GenerateCommitMessageArgs,
    ) -> GitMessageGenerator.GenerateCommitMessageResult:
        diff = subprocesses.check_output(
            'git',
            'diff',
            'HEAD',
            '--',
            ':(exclude)**/.manifests.json',
            cwd=args.cwd,
        ).decode()

        prompt = '\n\n'.join([
            'Write a short git commit message for the following git diff:',
            f'```\n{diff}\n```',
        ])

        with open(os.path.join(get_home_dir(), 'llm/.env')) as f:
            dotenv.Dotenv(stream=f).apply_to(os.environ)

        llm = OpenaiChatModel()

        resp = llm(
            [UserMessage(prompt)],
            *((MaxTokens(self._config.max_tokens),) if self._config.max_tokens is not None else ()),
        )
        resp_str = check.non_empty_str(resp.v[0].m.s)

        return GitMessageGenerator.GenerateCommitMessageResult(
            msg=resp_str,
            confirm=True,
        )


#


# @omlish-manifest
_AI_GIT_MESSAGE_GENERATOR_MANIFEST = GitMessageGeneratorManifest(
    mod_name=__name__,
    attr_name='AiGitMessageGenerator',
    name='ai',
)
