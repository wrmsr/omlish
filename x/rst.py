import contextlib
import io
import sys

import docutils.core


def rst2html(rst, report_level=None):
    kwargs = {
        'writer_name': 'html',
        'settings_overrides': {
            '_disable_config': True,
            'report_level': int(report_level) if report_level else 0
        }
    }
    target = io.StringIO()
    with contextlib.redirect_stderr(target):
        parts = docutils.core.publish_parts(rst, **kwargs)
        html = parts['html_body']
        warning = target.getvalue().strip()
        return html, warning


if __name__ == '__main__':
    html, warning = rst2html(sys.stdin.read())
    if warning:
        sys.stderr.write(warning)
    print(html)
