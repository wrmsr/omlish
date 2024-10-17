"""
TODO:
 - omdev/rst.py *and* rsttool.py, when we want extracted helpers
"""
import contextlib
import io
import sys

import docutils.core

from omlish import argparse as ap

from ..cli import CliModule


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


class Cli(ap.Cli):
    @ap.command(
        ap.arg('input-file', nargs='?'),
        ap.arg('--report-level', type=int),
    )
    def html(self) -> None:
        if self.args.input_file is not None:
            with open(self.args.input_file) as f:
                src = f.read()
        else:
            src = sys.stdin.read()

        html, warning = rst2html(
            src,
            report_level=self.args.report_level,
        )

        if warning:
            sys.stderr.write(warning)
        print(html)


# @omlish-manifest
_CLI_MODULE = CliModule('rst', __name__)


if __name__ == '__main__':
    Cli().call_and_exit()
