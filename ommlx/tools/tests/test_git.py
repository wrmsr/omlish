import os.path
import tempfile

import pytest

from omlish.secrets.tests.harness import HarnessSecrets
from omlish.subprocesses.sync import subprocesses

from ... import huggingface as hfu
from ..git import AiGitMessageGenerator
from ..git import GitAiBackend
from ..git import GitMessageGenerator
from ..git import MlxlmGitAiBackend
from ..git import OpenaiGitAiBackend


def _test_git_message_generator(backend: GitAiBackend) -> None:
    tmp_dir = tempfile.mkdtemp()

    subprocesses.check_call('git', 'init', cwd=tmp_dir)
    with open(os.path.join(tmp_dir, 'a'), 'w') as f:
        f.write('first\n')
    subprocesses.check_call('git', 'add', '.', cwd=tmp_dir)
    subprocesses.check_call('git', 'commit', '-m', 'initial', cwd=tmp_dir)

    with open(os.path.join(tmp_dir, 'a'), 'w') as f:
        f.write('second\n')

    args = GitMessageGenerator.GenerateCommitMessageArgs(
        cwd=tmp_dir,
    )

    gmg = AiGitMessageGenerator(backend=backend)

    result = gmg.generate_commit_message(args)

    print(result)


def test_git_message_generator_openai(harness):
    harness[HarnessSecrets].get_or_skip('openai_api_key')
    _test_git_message_generator(OpenaiGitAiBackend())


def test_git_message_generator_mlxlm():
    bg_cfg = MlxlmGitAiBackend.Config()

    try:
        import huggingface_hub  # noqa
    except ImportError:
        pytest.skip('no huggingface_hub')

    if not hfu.is_repo_cached(mdl := bg_cfg.model):
        pytest.skip(f'no model: {mdl}')

    _test_git_message_generator(MlxlmGitAiBackend(bg_cfg))
