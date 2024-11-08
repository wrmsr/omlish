"""
https://segno.readthedocs.io/en/stable/comparison-qrcode-libs.html
- https://github.com/nayuki/QR-Code-generator
- https://github.com/heuer/segno/
- https://github.com/lincolnloop/python-qrcode
"""
import argparse
import os
import subprocess
import sys
import tempfile
import typing as ta

from omlish import lang

from ..cli import CliModule


if ta.TYPE_CHECKING:
    import segno
else:
    segno = lang.proxy_import('segno')


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('content', nargs='?')

    parser.add_argument('-x', '--target-size', type=int)

    parser.add_argument('-o', '--output')
    parser.add_argument('-O', '--open', action='store_true')

    parser.add_argument(
        '--error', '-e',
        help=(
            'Error correction level: '
            '"L": 7%% (default), '
            '"M": 15%%, '
            '"Q": 25%%, '
            '"H": 30%%, '
            '"-": no error correction (used for M1 symbols)'
        ),
        choices=('L', 'M', 'Q', 'H', '-'),
    )
    args = parser.parse_args()

    if (content := args.content) is None:
        content = sys.stdin.read()

    qr = segno.make(content)

    if (tx := args.target_size) is not None:
        sz = max(*qr.symbol_size())
        sc = max(float(tx) / sz, 1)
    else:
        sc = 1

    if args.output is not None:
        out_file = args.output
    else:
        fd, out_file = tempfile.mkstemp(suffix='-qrcode.png')
        os.close(fd)

    qr.save(out_file, scale=sc)

    if args.output is None:
        print(out_file)

    if args.open:
        subprocess.check_call(['open', out_file])


# @omlish-manifest
_CLI_MODULE = CliModule('qr', __name__)


if __name__ == '__main__':
    _main()
