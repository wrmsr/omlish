"""
Imports given python modules, each in isolation, outputting for each:
 - "time" - time taken
 - "rss" - final RSS
 - "imported" - imported modules in import order

Can be run on external python interpreters.

TODO:
 - dump agg stats
 - graphviz
"""
import argparse
import dataclasses as dc
import inspect
import itertools
import json
import os
import re
import shlex
import subprocess
import sys
import typing as ta

from omlish import check
from omlish import lang
from omlish.concurrent import all as conc

from ...cli import CliModule


##


@dc.dataclass(frozen=True)
class Item:
    spec: str

    time: float
    rss: int
    imported: frozenset[str]


##


def _payload(specs) -> None:
    import resource
    import sys
    import time

    def get_rss() -> int:
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    start_modules = frozenset(sys.modules)
    start_rss = get_rss()
    start_time = time.time()

    for spec in specs:
        exec(f'import {spec}')

    end_time = time.time()
    end_rss = get_rss()
    end_modules = frozenset(sys.modules)

    import json

    def json_dumps(obj):
        return json.dumps(obj, indent=None, separators=(',', ':'))

    print(json_dumps({
        'time': end_time - start_time,
        'rss': end_rss - start_rss,
        'imported': sorted(end_modules - start_modules),
    }))


@lang.cached_function
def payload_src() -> str:
    return inspect.getsource(_payload)


def run_one(
        spec: str,
        *,
        shell_wrap: bool = True,
        python: str | None = None,
) -> Item:
    spec_payload_src = '\n\n'.join([
        payload_src(),
        f'_payload([{spec!r}])',
    ])

    args = [
        python or sys.executable,
        '-c',
        spec_payload_src,
    ]
    if shell_wrap:
        args = ['sh', '-c', ' '.join(map(shlex.quote, args))]

    output = subprocess.check_output(args)

    output_lines = output.decode().strip().splitlines()
    if not output_lines:
        raise Exception(f'no output: {spec}')
    if len(output_lines) > 1:
        print(f'warning: unexpected output: {spec}')

    dct = json.loads(output_lines[-1])
    return Item(
        spec=spec,
        **dct,
    )


##


def _find_root_specs(*roots: str) -> ta.Iterator[str]:
    stk: list[str] = list(reversed(roots))
    while stk:
        cur = stk.pop()
        if os.sep in cur:
            if os.path.isdir(cur):
                stk.extend(reversed([
                    os.path.join(cur, c)
                    for c in os.listdir(cur)
                ]))
                continue

            if not cur.endswith('.py'):
                continue

            spec = cur.rpartition('.')[0].replace(os.sep, '.')

        else:
            spec = cur

        yield spec


def run(
        *,
        roots: lang.SequenceNotStr[str] | None = None,
        modules: lang.SequenceNotStr[str] | None = None,

        filters: ta.Iterable[str] | None = None,
        num_threads: int | None = 0,

        **kwargs: ta.Any,
) -> ta.Mapping[str, Item]:
    filter_pats = [re.compile(f) for f in filters or []]

    specs: list[str] = []
    for spec in itertools.chain(
        *([_find_root_specs(*check.not_isinstance(roots, str))] if roots is not None else []),
        *([check.not_isinstance(modules, str)] if modules is not None else []),
    ):
        if any(p.fullmatch(spec) for p in filter_pats):
            continue

        specs.append(spec)

    out: dict[str, Item] = {}
    with conc.new_executor(num_threads) as ex:
        futs = [ex.submit(run_one, spec, **kwargs) for spec in specs]
        for fut in futs:
            item = fut.result()
            out[item.spec] = item

    return out


##


# @omlish-manifest
_CLI_MODULE = CliModule('py/importscan', __name__)


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--jobs', type=int)
    parser.add_argument('-f', '--filter', action='append')
    parser.add_argument('-t', '--filter-tests', action='store_true')
    parser.add_argument('--python', default=sys.executable)
    parser.add_argument('-m', '--module', action='append')
    parser.add_argument('root', nargs='*')
    args = parser.parse_args()

    filters = [*(args.filter or [])]
    if args.filter_tests:
        filters.extend([
            r'.*\.conftest',
            r'.*\.tests\..*',
        ])

    for item in run(
            roots=args.root,
            modules=args.module,
            filters=filters,
            num_threads=args.jobs,
            python=args.python,
    ).values():
        print(json.dumps(dc.asdict(item)))


if __name__ == '__main__':
    _main()
