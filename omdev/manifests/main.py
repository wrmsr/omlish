import argparse
import asyncio
import dataclasses as dc
import multiprocessing as mp
import os.path

from omlish.lite.json import json_dumps_pretty
from omlish.logs.standard import configure_standard_logging

from .building import ManifestBuilder
from .building import check_package_manifests


##


def _get_base_dir(args) -> str:
    if args.base is not None:
        base = args.base
    else:
        base = os.getcwd()
    base = os.path.abspath(base)
    if not os.path.isdir(base):
        raise RuntimeError(base)
    return base


def _gen_cmd(args) -> None:
    base_dir = _get_base_dir(args)

    jobs = args.jobs or int(max(mp.cpu_count() // 1.5, 1))
    builder = ManifestBuilder(
        base_dir,
        jobs,
    )

    async def do():
        return await asyncio.gather(*[
            builder.build_package_manifests(
                pkg,
                write=bool(args.write),
            )
            for pkg in args.package
        ])

    mss = asyncio.run(do())
    if not args.quiet:
        for ms in mss:
            print(json_dumps_pretty([dc.asdict(m) for m in ms]))


def _check_cmd(args) -> None:
    base_dir = _get_base_dir(args)

    for pkg in args.package:
        check_package_manifests(
            pkg,
            base_dir,
        )


def _main(argv=None) -> None:
    configure_standard_logging('INFO')

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_gen = subparsers.add_parser('gen')
    parser_gen.add_argument('-b', '--base')
    parser_gen.add_argument('-w', '--write', action='store_true')
    parser_gen.add_argument('-q', '--quiet', action='store_true')
    parser_gen.add_argument('-j', '--jobs', type=int)
    parser_gen.add_argument('package', nargs='*')
    parser_gen.set_defaults(func=_gen_cmd)

    parser_check = subparsers.add_parser('check')
    parser_check.add_argument('-b', '--base')
    parser_check.add_argument('package', nargs='*')
    parser_check.set_defaults(func=_check_cmd)

    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
