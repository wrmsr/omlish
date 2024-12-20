"""
TODO:
 - omdev/rst.py *and* rsttool.py, when we want extracted helpers
"""
import contextlib
import io
import os.path
import subprocess
import sys
import tempfile
import typing as ta

from omlish import check
from omlish import lang
from omlish.argparse import all as ap

from ..cli import CliModule


if ta.TYPE_CHECKING:
    import docutils.core
    import markdown
else:
    docutils = lang.proxy_import('docutils', extras=['core'])
    markdown = lang.proxy_import('markdown')


def rst2html(rst, report_level=None):
    kwargs = {
        'writer_name': 'html',
        'settings_overrides': {
            '_disable_config': True,
            'report_level': int(report_level) if report_level else 0,
        },
    }

    target = io.StringIO()
    with contextlib.redirect_stderr(target):
        parts = docutils.core.publish_parts(rst, **kwargs)  # type: ignore
        html = parts['html_body']
        warning = target.getvalue().strip()
        return html, warning


def open_html(src: str, name: str) -> None:
    check.non_empty_str(name)
    out_dir = tempfile.mkdtemp()
    out_file = os.path.join(out_dir, name + '.html')
    with open(out_file, 'w') as f:
        f.write(src)
    subprocess.check_call(['open', out_file])


class Cli(ap.Cli):
    def _read_file(self, input_file: str | None) -> tuple[str, str]:
        if input_file is not None:
            with open(input_file) as f:
                src = f.read()
            name = os.path.basename(input_file)

        else:
            src = sys.stdin.read()
            name = 'stdin'

        return src, name

    @ap.cmd(
        ap.arg('input-file', nargs='?'),
        ap.arg('--report-level', type=int),
        ap.arg('-O', '--open', action='store_true'),
    )
    def rst(self) -> None:
        src, name = self._read_file(self.args.input_file)

        html, warning = rst2html(
            src,
            report_level=self.args.report_level,
        )

        if warning:
            sys.stderr.write(warning)

        if self.args.open:
            open_html(html, name)
        else:
            print(html)

    @ap.cmd(
        ap.arg('input-file', nargs='?'),
        ap.arg('-O', '--open', action='store_true'),
    )
    def md(self):
        src, name = self._read_file(self.args.input_file)

        html = markdown.markdown(src)

        if self.args.open:
            open_html(html, name)
        else:
            print(html)


# @omlish-manifest
_CLI_MODULE = CliModule('doc', __name__)


if __name__ == '__main__':
    Cli()(exit=True)
