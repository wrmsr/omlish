"""
TODO:
 - a general purpose profile tool lol - or is this for / in bootstrap?
"""
import os.path
import subprocess
import sys
import tempfile

from omlish.argparse import all as ap

from ..cli import CliModule


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('file'),
        ap.arg('out-file', nargs='?'),
        ap.arg('-w', '--write', action='store_true'),
        ap.arg('-o', '--open', action='store_true'),
        ap.arg('-O', '--overwrite', action='store_true'),
    )
    def pstats_pdf(self) -> None:
        out_file = self.args.out_file
        if out_file is None and self.args.write:
            out_file = self.args.file + '.pdf'

        if out_file is not None:
            if os.path.exists(out_file) and not self.args.overwrite:
                raise OSError(f'File exists: {out_file}')
        else:
            out_file = tempfile.mktemp(suffix=os.path.basename(self.args.file) + '.pdf')  # noqa

        dot = subprocess.check_output([
            sys.executable,
            '-m', 'gprof2dot',
            '-f', 'pstats',
            self.args.file,
        ])

        pdf = subprocess.check_output(
            ['dot', '-Tpdf'],
            input=dot,
        )

        with open(out_file, 'wb') as f:
            f.write(pdf)
        print(out_file)

        if self.args.open:
            subprocess.check_call(['open', out_file])


# @omlish-manifest
_CLI_MODULE = CliModule('prof', __name__)


if __name__ == '__main__':
    Cli()()
