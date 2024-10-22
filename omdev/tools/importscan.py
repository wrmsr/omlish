"""
TODO:
 - dump agg stats
 - graphviz
"""
import argparse
import dataclasses as dc
import inspect
import json
import os
import re
import shlex
import subprocess
import sys
import typing as ta

from omlish import concurrent as cu
from omlish import lang

from ..cli import CliModule


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


def _find_specs(
        *roots: str,
        filters: ta.Iterable[str] | None = None,
) -> ta.Sequence[str]:
    filter_pats = [re.compile(f) for f in filters or []]

    out: list[str] = []
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

        if any(p.fullmatch(spec) for p in filter_pats):
            continue

        out.append(spec)

    return out


def run(
        *roots: str,
        filters: ta.Iterable[str] | None = None,
        num_threads: int | None = 0,
        **kwargs: ta.Any,
) -> ta.Mapping[str, Item]:
    specs = _find_specs(*roots, filters=filters)

    out: dict[str, Item] = {}
    with cu.new_executor(num_threads) as ex:
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
    parser.add_argument('root', nargs='+')
    args = parser.parse_args()

    filters = [*(args.filter or [])]
    if args.filter_tests:
        filters.extend([
            r'.*\.conftest',
            r'.*\.tests\..*',
        ])

    for item in run(
            *args.root,
            filters=filters,
            num_threads=args.jobs,
            python=args.python,
    ).values():
        print(json.dumps(dc.asdict(item)))


if __name__ == '__main__':
    _main()
