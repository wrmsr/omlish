from omcore.argparse import all as ap
from omcore.formats.json import all as json

from .paths import HomePaths
from .paths import get_home_paths


##


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('kind', choices=[
            e.lower()
            for e in HomePaths.DirKind.__members__
        ], nargs='?'),
        name='dir',
    )
    def dir_cmd(self) -> None:
        hp = get_home_paths()
        if (dka := self.args.kind) is not None:
            print(hp.get_dir(HomePaths.DirKind[dka.upper()]))
        else:
            print(json.dumps_pretty({
                dkn.lower(): hp.get_dir(dk)
                for dkn, dk in HomePaths.DirKind.__members__.items()
            }))


def _main() -> None:
    Cli()()


if __name__ == '__main__':
    _main()
