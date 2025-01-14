"""
Conventions:
 - must import whole global modules, if aliased must all match
 - must import 'from' items for local modules

TODO:
 - !! check only importing lite code
 - check no rel impots
 - !! strip manifests? or relegate them to a separate tiny module ala __main__.py?
  - # @omlish-no-amalg ? in cli.types? will strip stmt (more than 1 line) following @manifest, so shouldn't import
 - more sanity checks lol
 - typealias - support # noqa, other comments, and lamely support multiline by just stealing lines till it parses
 - remove `if __name__ == '__main__':` blocks - thus, convention: no def _main() for these

See:
 - https://github.com/xonsh/amalgamate - mine is for portability not speed, and doesn't try to work on unmodified code

Targets:
 - interp
 - pyproject
 - precheck
 - build
 - pyremote
 - bootstrap
 - deploy
 - supervisor?
"""
import argparse
import logging
import os.path
import stat
import typing as ta

from omlish import check
from omlish.logs import all as logs

from .gen import SCAN_COMMENT
from .gen import AmalgGenerator


log = logging.getLogger(__name__)


##


def _gen_one(
        input_path: str,
        output_path: str | None,
        *,
        mounts: ta.Mapping[str, str],
) -> None:
    log.info('Generating: %s -> %s', input_path, output_path)

    src = AmalgGenerator(
        input_path,
        mounts=mounts,
        output_dir=os.path.dirname(output_path if output_path is not None else input_path),
    ).gen_amalg()

    if output_path is not None:
        with open(output_path, 'w') as f:
            f.write(src)

        src_mode = os.stat(input_path).st_mode
        out_mode = (
            src_mode
            | (stat.S_IXUSR if src_mode & stat.S_IRUSR else 0)
            | (stat.S_IXGRP if src_mode & stat.S_IRGRP else 0)
            | (stat.S_IXOTH if src_mode & stat.S_IROTH else 0)
        )
        os.chmod(output_path, out_mode)

    else:
        print(src)


def _scan_one(
        input_path: str,
        **kwargs: ta.Any,
) -> None:
    if not input_path.endswith('.py'):
        return

    with open(input_path) as f:
        src = f.read()

    sls = [l for l in src.splitlines() if l.startswith(SCAN_COMMENT)]
    for sl in sls:
        sas = sl[len(SCAN_COMMENT):].split()
        if len(sas) != 1:
            raise Exception(f'Invalid scan args: {input_path=} {sas=}')

        output_path = os.path.abspath(os.path.join(os.path.dirname(input_path), sas[0]))
        _gen_one(
            input_path,
            output_path,
            **kwargs,
        )


def _gen_cmd(args) -> None:
    if not os.path.isfile('pyproject.toml'):
        raise Exception('Not in project root')

    mounts = {}
    for m in args.mounts or ():
        if ':' not in m:
            mounts[m] = os.path.abspath(m)
        else:
            k, v = m.split(':')
            mounts[k] = os.path.abspath(v)

    for i in args.inputs:
        if os.path.isdir(i):
            log.info('Scanning %s', i)
            for we_dirpath, we_dirnames, we_filenames in os.walk(i):  # noqa
                for fname in we_filenames:
                    _scan_one(
                        os.path.abspath(os.path.join(we_dirpath, fname)),
                        mounts=mounts,
                    )

        else:
            output_dir = args.output
            if output_dir is not None:
                output_path = check.isinstance(os.path.join(output_dir, os.path.basename(i)), str)
            else:
                output_path = None

            _gen_one(
                os.path.abspath(i),
                output_path,
                mounts=mounts,
            )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_gen = subparsers.add_parser('gen')
    parser_gen.add_argument('--mount', '-m', dest='mounts', action='append')
    parser_gen.add_argument('--output', '-o')
    parser_gen.add_argument('inputs', nargs='+')
    parser_gen.set_defaults(func=_gen_cmd)

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
