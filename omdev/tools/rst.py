import argparse
import contextlib
import io
import sys

import docutils.core


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


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('input', nargs='?')
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            src = f.read()
    else:
        src = sys.stdin.read()

    html, warning = rst2html(src)
    if warning:
        sys.stderr.write(warning)
    print(html)


if __name__ == '__main__':
    _main()
