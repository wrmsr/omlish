import typing as ta

from omcore import check
from omcore.argparse import all as ap

from ..configs import EntrypointConfig
from ..profiles import Profile
from .configs import EmbeddingConfig


##


class EmbeddingProfile(Profile):
    def configure(self, argv: ta.Sequence[str]) -> EntrypointConfig:
        parser = ap.ArgumentParser()
        parser.add_argument('prompt', nargs='*')
        parser.add_argument('-b', '--backend', default='openai')
        args = parser.parse_args(argv)

        content = ' '.join(args.prompt)

        cfg = EmbeddingConfig(
            content=check.non_empty_str(content),
            backend=args.backend,
        )

        return cfg
