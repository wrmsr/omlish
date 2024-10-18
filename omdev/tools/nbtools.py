"""
TODO:
 - try to keep comments, option to strip em
 - also trim ws on either side of blocks
"""
import io
import json
import os.path
import subprocess
import sys
import urllib.parse
import urllib.request

from omlish import argparse as ap
from omlish import check

from ..cli import CliModule


class Cli(ap.Cli):
    @ap.command(
        ap.arg('file'),
        ap.arg('-w', '--write', action='store_true'),
        ap.arg('-o', '--overwrite', action='store_true'),
        ap.arg('--no-header', action='store_true'),
        ap.arg('--keep-bangs', action='store_true'),
        ap.arg('--black', action='store_true'),
    )
    def strip_code(self) -> None:
        out_file: str | None = None
        out_header: list[str] = []

        if ':' in self.args.file:
            url = self.args.file
            pu = urllib.parse.urlparse(url)
            check.equal(pu.scheme, 'https')

            out_header.append(f'# Origin: {url}')

            if pu.hostname == 'github.com':
                _, user, repo, blob, *rest = pu.path.split('/')
                check.equal(blob, 'blob')
                url = f'https://raw.githubusercontent.com/{user}/{repo}/refs/heads/{"/".join(rest)}'

            elif pu.hostname == 'raw.githubusercontent.com':
                pass

            else:
                raise ValueError(pu.hostname)

            file = pu.path.split('/')[-1]
            check.state(file.endswith('.ipynb'))

            if self.args.write:
                out_file = file.rpartition('.')[0] + '.py'

            with urllib.request.urlopen(url) as resp:  # noqa
                buf = resp.read()

            dct = json.loads(buf.decode('utf-8'))

        elif self.args.file == '-':
            if self.args.write:
                raise Exception('Write not supported with stdin')

            dct = json.load(sys.stdin)

        else:
            with open(self.args.file) as f:
                dct = json.load(f)

            if self.args.write:
                out_file = self.args.file.rpartition('.')[0] + '.py'

        if out_file is not None and os.path.isfile(out_file) and not self.args.overwrite:
            raise OSError(f'File exists: {out_file}')

        delim = '\n##\n\n'

        out = io.StringIO()
        if not self.args.no_header and out_header:
            out.write('\n'.join(out_header))
            out.write(delim)

        code_cells = [c for c in dct['cells'] if c['cell_type'] == 'code']
        for i, c in enumerate(code_cells):
            if i:
                out.write(delim)

            src = ''.join(c['source'])
            if not self.args.keep_bangs:
                src = ''.join(
                    ('# ' + l) if l.startswith('!') else l
                    for l in src.splitlines(keepends=True)
                )

            out.write(src)
            out.write('\n')

        out_src = out.getvalue()

        if self.args.black:
            proc = subprocess.run(
                [sys.executable, '-m', 'black', '-'],
                input=out_src.encode('utf-8'),
                stdout=subprocess.PIPE,
                check=True,
            )
            out_src = proc.stdout.decode('utf-8')

        if out_file is not None:
            with open(out_file, 'w') as f:
                f.write(out_src)
            print(f'Wrote {out_file}')

        else:
            sys.stdout.write(out_src)


# @omlish-manifest
_CLI_MODULE = CliModule(['notebook', 'nb'], __name__)


if __name__ == '__main__':
    Cli()()
