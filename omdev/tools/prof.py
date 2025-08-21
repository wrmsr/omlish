"""
TODO:
 - a general purpose profile tool lol - or is this for / in bootstrap?
"""
import os.path
import shutil
import subprocess
import sys
import tempfile

from omlish.argparse import all as ap

from ..cli import CliModule


##


def pstats_to_pdf(
        pstats_file: str,
        pdf_file: str,
) -> None:
    dot = subprocess.check_output([
        sys.executable,
        '-m', 'gprof2dot',
        '-f', 'pstats',
        pstats_file,
    ])

    pdf = subprocess.check_output(
        ['dot', '-Tpdf'],
        input=dot,
    )

    with open(pdf_file, 'wb') as f:
        f.write(pdf)


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('pstats-file'),
        ap.arg('pdf-file', nargs='?'),
        ap.arg('-w', '--write', action='store_true'),
        ap.arg('-o', '--open', action='store_true'),
        ap.arg('-O', '--overwrite', action='store_true'),
    )
    def pstats_pdf(self) -> None:
        pdf_file = self.args.pdf_file
        if pdf_file is None and self.args.write:
            pdf_file = self.args.pstats_file + '.pdf'

        if pdf_file is not None:
            if os.path.exists(pdf_file) and not self.args.overwrite:
                raise OSError(f'File exists: {pdf_file}')
        else:
            pdf_file = tempfile.mktemp(suffix=os.path.basename(self.args.pstats_file) + '.pdf')  # noqa

        pstats_to_pdf(
            self.args.pstats_file,
            self.args.pdf_file,
        )

        print(pdf_file)

        if self.args.open:
            subprocess.check_call(['open', pdf_file])

    @ap.cmd(
        ap.arg('src'),
        ap.arg('out-file', nargs='?'),
        ap.arg('-p', '--pdf', action='store_true'),
        ap.arg('-o', '--open', action='store_true'),
        ap.arg('-O', '--overwrite', action='store_true'),
        ap.arg('-x', '--exe'),
    )
    def pstats_exec(self) -> None:
        if self.args.out_file is not None:
            if os.path.exists(self.args.out_file) and not self.args.overwrite:
                raise OSError(f'File exists: {self.args.out_file}')

        tmp_dir = tempfile.mkdtemp()

        src_file = os.path.join(tmp_dir, 'pstats_exec.py')
        with open(src_file, 'w') as f:
            f.write(self.args.src)

        pstats_file = os.path.join(tmp_dir, 'prof.pstats')

        if (exe := self.args.exe) is None:
            exe = sys.executable

        # TODO: --python - and handle env vars, unset venv and pythonpath stuff - helper for this, scrub env
        #  - share with execstat, -x
        subprocess.check_call([
            exe,
            '-m', 'cProfile',
            '-o', pstats_file,
            os.path.abspath(src_file),
        ])

        if self.args.pdf:
            out_file = os.path.join(tmp_dir, 'pstats.pdf')

            pstats_to_pdf(
                pstats_file,
                out_file,
            )

        else:
            out_file = pstats_file

        if self.args.out_file is not None:
            shutil.move(out_file, self.args.out_file)
            out_file = self.args.out_file

        print(out_file)

        if self.args.open:
            if self.args.pdf:
                subprocess.check_call(['open', out_file])

            else:
                # Alt: python -i <setup.py> where setup.py is 'import pstats; stats = pstats.Stats(<out_file>)'
                os.execl(
                    exe,
                    exe,
                    '-m', 'pstats',
                    out_file,
                )


# @omlish-manifest
_CLI_MODULE = CliModule('prof', __name__)


if __name__ == '__main__':
    Cli()()
