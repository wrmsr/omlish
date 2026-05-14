#!/usr/bin/env python3
# ruff: noqa: UP037 UP045
# @omlish-lite
# @omlish-script
import argparse
import inspect
import json
import os.path
import statistics
import subprocess
import sys
import tempfile
import typing as ta


##


class Tracker:
    def __init__(
            self,
            *,
            time: bool = False,
            rss: bool = False,
            modules: bool = False,
    ) -> None:
        super().__init__()

        self._stats: 'list[Tracker.Stat]' = [
            *([self.Rss()] if rss else []),
            *([self.Time()] if time else []),
            *([self.Modules()] if modules else []),
        ]

    #

    class Stat:
        name: str

        @classmethod
        def measure(cls) -> 'ta.Any':
            raise NotImplementedError

        @classmethod
        def diff(cls, new: 'ta.Any', old: 'ta.Any') -> 'ta.Any':
            raise NotImplementedError

        _start: 'ta.Any'

        def start(self) -> None:
            self._start = self.measure()

        _end: 'ta.Any'

        def end(self) -> None:
            self._end = self.measure()

        def report(self) -> 'dict[str, ta.Any]':
            return {self.name: self.diff(self._end, self._start)}

    #

    class Rss(Stat):
        name = 'rss'

        @classmethod
        def measure(cls) -> int:
            import resource  # noqa
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        @classmethod
        def diff(cls, new: int, old: int) -> int:
            return new - old

    #

    class Time(Stat):
        name = 'time'

        @classmethod
        def measure(cls) -> float:
            import time  # noqa
            return time.monotonic()

        @classmethod
        def diff(cls, new: float, old: float) -> float:
            return new - old

    #

    class Modules(Stat):
        name = 'modules'

        @classmethod
        def measure(cls) -> 'ta.Sequence[str]':
            import sys
            return list(sys.modules)

        @classmethod
        def diff(cls, new: 'ta.Sequence[str]', old: 'ta.Sequence[str]') -> 'ta.Sequence[str]':
            old_set = set(old)
            return [mod for mod in new if mod not in old_set]

    #

    def start(self) -> None:
        for st in self._stats:
            st.start()

    def end(self) -> None:
        for st in self._stats:
            st.end()

    def report(self) -> 'dict[str, ta.Any]':
        return {k: v for st in self._stats for k, v in st.report().items()}

    #

    def exec(
            self,
            src: str,
            *,
            setup: 'ta.Optional[str]' = None,
            report: 'ta.Optional[ta.Callable[[dict], None]]' = None,
    ) -> 'dict[str, ta.Any]':
        ns: dict = {}

        if setup:
            exec(setup, globals(), ns)

        code = compile(src, '', 'exec')

        self.start()

        ret: 'ta.Any' = None

        try:
            exec(code, globals(), ns)

            self.end()

            ret = self.report()

            return ret

        finally:
            self.end()

            if report is not None:
                if ret is None:
                    self.end()

                    ret = self.report()

                report(ret)


#


# @omlish-manifest
_CLI_MODULE = {'!.cli.types.CliModule': {
    'name': 'py/execstat',
    'module': __name__,
}}


def _main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('src')
    parser.add_argument('-s', '--setup')

    parser.add_argument('-t', '--time', action='store_true')
    parser.add_argument('-r', '--rss', action='store_true')
    parser.add_argument('-m', '--modules', action='store_true')
    parser.add_argument('-M', '--modules-ordered', action='store_true')

    parser.add_argument('-n', '--num-runs', type=int, default=1)

    parser.add_argument('-P', '--precision', type=int, default=3)

    parser.add_argument('--out-dir')

    parser.add_argument('-x', '--exe')

    args = parser.parse_args()

    if (n := args.num_runs) < 1:
        raise ValueError('num-runs must be > 0')

    prec = args.precision

    #

    if (exe := args.exe) is None:
        exe = sys.executable

    if (out_dir := args.out_dir) is None:
        out_dir = tempfile.mkdtemp()

    results = []
    for i in range(n):
        out_file = os.path.join(out_dir, f'{str(i).zfill(len(str(n)))}.json')

        tkr_kw = dict(
            time=bool(args.time),
        )

        run_kw = dict(
            src=args.src,
            setup=args.setup,
        )

        if i == 0:
            tkr_kw.update(
                rss=bool(args.rss),
                modules=bool(args.modules) or bool(args.modules_ordered),
            )

        payload = '\n'.join([
            inspect.getsource(Tracker),
            '',
            '',
            f'with open({out_file!r}, "w") as f:',
            f'    Tracker(**{tkr_kw!r}).exec(',
            f'        **{run_kw!r},',
            f'        report=lambda dct: f.write(__import__("json").dumps(dct)),',
            f'    )',
        ])

        subprocess.call([exe, '-c', payload])

        with open(out_file) as f:
            result = json.load(f)

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

    if args.modules or args.modules_ordered:
        mods = results[0]['modules']
        out.update({
            'num_modules': len(mods),
        })
        if args.modules:
            out.update({
                'modules': sorted(mods),
            })
        if args.modules_ordered:
            out.update({
                'modules_ordered': mods,
            })

    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    _main()
