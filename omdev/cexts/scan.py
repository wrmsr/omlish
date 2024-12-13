import argparse
import logging
import os.path
import typing as ta

from omlish.logs import all as logs

from .magic import CextMagic


log = logging.getLogger(__name__)


def scan_one(
        input_path: str,
        **kwargs: ta.Any,
) -> None:
    if not any(input_path.endswith('.' + fx) for fx in CextMagic.STYLE.exts):
        return

    with open(input_path, 'rb') as f:
        srcb = f.read()

    try:
        src = srcb.decode('utf-8')
    except UnicodeDecodeError:
        return

    sls = [l for l in src.splitlines() if l.startswith('// ' + CextMagic.KEY)]  # FIXME
    for sl in sls:
        sas = sl[len(CextMagic.KEY) + 3:].split()  # noqa

        log.info('Found ext: %s', input_path)


def _scan_cmd(args) -> None:
    for i in args.inputs:
        if not os.path.isdir(i):
            raise Exception(f'Not a directory: {i}')

        log.info('Scanning %s', i)
        for we_dirpath, we_dirnames, we_filenames in os.walk(i):  # noqa
            for fname in we_filenames:
                scan_one(
                    os.path.abspath(os.path.join(we_dirpath, fname)),
                )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_scan = subparsers.add_parser('scan')
    parser_scan.add_argument('inputs', nargs='+')
    parser_scan.set_defaults(func=_scan_cmd)

    return parser


def _main() -> None:
    logs.configure_standard_logging('INFO')

    parser = _build_parser()
    args = parser.parse_args()
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
