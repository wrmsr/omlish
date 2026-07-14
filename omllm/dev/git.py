"""
TODO:
 - move omit magic to omdev lol
"""
import os.path
import typing as ta

from omdev.git.magic import GIT_DIFF_OMIT_MAGIC_COMMENT
from omdev.py.srcheaders import get_py_header_lines
from omdev.tools.git.messages import GitMessageGenerator
from omlish import check
from omlish import lang
from omlish.http import all as http
from omlish.subprocesses.sync import subprocesses


with lang.auto_proxy_import(globals()):
    from .. import llm


##


# @omlish-manifest omdev.tools.git.messages.GitMessageGeneratorManifest(name='llm')
class LlmGitMessageGenerator(GitMessageGenerator):
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

    def _build_prompt(self, args: GitMessageGenerator.GenerateCommitMessageArgs) -> str:
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

        # deleted_prompt: str | None = None
        # if deleted_files := [fn for fn in diff_files if not os.path.isfile(fn)]:
        #     deleted_prompt = '\n'.join([
        #         'Additionally, the following files were deleted:',
        #         *([f'- {fn}' for fn in deleted_files]),
        #     ])

        return '\n\n'.join([
            'Write a short git commit message for the following git diff:',
            f'```\n{diff}\n```',
            # *([deleted_prompt] if deleted_prompt else []),
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

    #

    def generate_commit_message(
            self,
            args: GitMessageGenerator.GenerateCommitMessageArgs,
    ) -> GitMessageGenerator.GenerateCommitMessageResult:
        prompt = self._build_prompt(args)

        #

        from omdev.home.secrets import load_secrets

        api_key = load_secrets().get('openai_api_key')

        #

        svc = llm.CompletionOpenaiBackend(
            api_key=api_key,
            http_client=http.SyncAsyncHttpClient(http.client()),
        )

        resp = lang.sync_await(svc.complete(llm.Context(
            messages=[
                llm.UserMessage(prompt),
            ],
        )))

        msg = check.isinstance(check.single(resp.c), llm.TextContent).s

        #

        return GitMessageGenerator.GenerateCommitMessageResult(
            msg=msg,
            confirm=True,
        )
