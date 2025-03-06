import os.path
import tempfile

from omdev.tools.git.messages import GitMessageGenerator
from omlish.secrets.tests.harness import HarnessSecrets
from omlish.subprocesses.sync import subprocesses

from ..git import AiGitMessageGenerator


def test_git(harness):
    harness[HarnessSecrets].get_or_skip('openai_api_key')

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

    gmg = AiGitMessageGenerator()

    result = gmg.generate_commit_message(args)

    print(result)
