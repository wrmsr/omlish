import io
import json
import os.path
import sys

from omlish import argparse as ap

from ..cli import CliModule


class Cli(ap.Cli):
    @ap.command(
        ap.arg('file'),
        ap.arg('-w', '--write', action='store_true'),
        ap.arg('-o', '--overwrite', action='store_true'),
    )
    def code(self) -> None:
        if self.args.write:
            out_file = self.args.file.rpartition('.')[0] + '.py'
            if os.path.isfile(out_file) and not self.args.overwrite:
                raise OSError(f'File exists: {out_file}')
        else:
            out_file = None

        with open(self.args.file) as f:
            dct = json.load(f)

        out = io.StringIO()
        code_cells = [c for c in dct['cells'] if c['cell_type'] == 'code']
        for i, c in enumerate(code_cells):
            if i:
                out.write('\n##\n\n')
            out.write(''.join(c['source']))
            out.write('\n')

        if out_file is not None:
            with open(out_file, 'w') as f:
                f.write(out.getvalue())
            print(f'Wrote {out_file}')
        else:
            sys.stdout.write(out.getvalue())


# @omlish-manifest
_CLI_MODULE = CliModule(['notebook', 'nb'], __name__)


if __name__ == '__main__':
    Cli()()
