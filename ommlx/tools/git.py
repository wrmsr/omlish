from omdev.tools.git.messages import GitMessageGenerator
from omdev.tools.git.messages import GitMessageGeneratorManifest


##


class AiGitMessageGenerator(GitMessageGenerator):
    def generate_commit_message(self) -> str:
        raise NotImplementedError


#


# @omlish-manifest
_AI_GIT_MESSAGE_GENERATOR_MANIFEST = GitMessageGeneratorManifest(
    mod_name=__name__,
    attr_name='AiGitMessageGenerator',
    name='ai',
)
