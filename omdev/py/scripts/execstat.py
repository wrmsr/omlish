#!/usr/bin/env python3
# @omlish-script
import argparse
import inspect
import json
import statistics
import subprocess
import sys


##


def _run(
        src: str,
        *,
        setup: str | None = None,
        time: bool = False,
        rss: bool = False,
        modules: bool = False,
) -> dict:
    if rss:
        import resource  # noqa

        def get_rss() -> int:
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    if time:
        from time import monotonic as get_time

    if modules:
        import sys  # noqa

        def get_modules() -> set[str]:
            return set(sys.modules)

    #

    if setup:
        exec(setup)

    code = compile(src, '', 'exec')

    #

    if rss:
        start_rss = get_rss()  # noqa

    if modules:
        start_modules = get_modules()  # noqa

    if time:
        start_time = get_time()  # noqa

    #

    exec(code)

    #

    if time:
        end_time = get_time()

    if rss:
        end_rss = get_rss()

    if modules:
        end_modules = get_modules()

    #

    return {
        **({'time': (end_time - start_time)} if time else {}),  # noqa
        **({'rss': (end_rss - start_rss)} if rss else {}),  # noqa
        **({'modules': sorted(end_modules - start_modules)} if modules else {}),  # noqa
    }


#


# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': 'py/execstat',
    'mod_name': __name__,
}}


def _main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('src')
    parser.add_argument('-s', '--setup')

    parser.add_argument('-t', '--time', action='store_true')
    parser.add_argument('-r', '--rss', action='store_true')
    parser.add_argument('-m', '--modules', action='store_true')

    parser.add_argument('-n', '--num-runs', type=int, default=1)

    parser.add_argument('-P', '--precision', type=int, default=3)

    parser.add_argument('-x', '--exe')

    args = parser.parse_args()

    if (n := args.num_runs) < 1:
        raise ValueError('num-runs must be > 0')

    prec = args.precision

    #

    if (exe := args.exe) is None:
        exe = sys.executable

    results = []
    for i in range(n):
        run_kw = dict(
            src=args.src,
            setup=args.setup,
            time=bool(args.time),
        )

        if i == 0:
            run_kw.update(
                rss=bool(args.rss),
                modules=bool(args.modules),
            )

        payload = '\n'.join([
            inspect.getsource(_run),
            f'dct = _run(**{run_kw!r})',
            'import json',
            'print(json.dumps(dct))',
        ])

        result = json.loads(subprocess.check_output([exe, '-c', payload]))

        results.append(result)

    #

    out = {}

    if args.time:
        if n > 1:
            ts = [r['time'] * 1000. for r in results]
            out.update({
                'time_ms_mean': (time_ms_mean := round(statistics.mean(ts), prec)),
                'time_ms_mean_s': f'{time_ms_mean:_}',
                'time_ms_median': (time_ms_median := round(statistics.median(ts), prec)),
                'time_ms_median_s': f'{time_ms_median:_}',
                'time_ms_quantiles': (time_ms_quantiles := [round(tq, prec) for tq in statistics.quantiles(ts)]),
                'time_ms_quantiles_s': [f'{tq:_}' for tq in time_ms_quantiles],
            })
        else:
            out.update({
                'time_ms': (time_ms := round(results[0]['time'] * 1000., prec)),
                'time_ms_s': f'{time_ms:_}',
            })

    if args.rss:
        out.update({
            'rss': (rss := results[0]['rss']),
            'rss_s': f'{rss:_}',
        })

    if args.modules:
        out.update({
            'modules': results[0]['modules'],
        })

    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    _main()
