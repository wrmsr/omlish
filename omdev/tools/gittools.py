import subprocess

from omlish import argparse as ap
from omlish import logs


class Cli(ap.Cli):
    @ap.command()
    def blob_sizes(self) -> None:
        # https://stackoverflow.com/a/42544963
        subprocess.check_call(  # noqa
            "git rev-list --objects --all | "
            "git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | "
            "sed -n 's/^blob //p' | "
            "sort --numeric-sort --key=2",
            shell=True,
        )


if __name__ == '__main__':
    logs.configure_standard_logging('INFO')
    Cli()()
