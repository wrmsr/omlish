"""
*not* trace - for each importable module (filterable, no tests/conftest) list:
 - post-import rss
 - time taken
 - modules imported
"""
import dataclasses as dc
import inspect
import json
import subprocess
import sys
import typing as ta


@dc.dataclass(frozen=True)
class Item:
    name: str

    time: float
    rss: int
    imported: frozenset[str]


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


def _main() -> None:
    payload_src = inspect.getsource(_payload)

    for spec in [
        'omlish.lang',
    ]:
        spec_payload_src = '\n\n'.join([
            payload_src,
            f'_payload([{spec!r}])',
        ])
        output = subprocess.check_output([
            sys.executable,
            '-c',
            spec_payload_src,
        ])
        output_lines = output.decode().strip().splitlines()
        if not output_lines:
            raise Exception(f'no output: {spec}')
        if len(output_lines) > 1:
            print(f'warning: unexpected output: {spec}')
        dct = json.loads(output_lines[-1])
        print((spec, dct))


if __name__ == '__main__':
    _main()
