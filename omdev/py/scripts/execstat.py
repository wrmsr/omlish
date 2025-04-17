#!/usr/bin/env python3
# @omlish-script
import inspect
import json
import subprocess
import sys


##


def _run(
        src: str,
        *,
        pre: str | None = None,
) -> dict:
    import resource  # noqa
    import sys  # noqa
    import time  # noqa

    def get_rss() -> int:
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    if pre:
        exec(pre)

    start_modules = set(sys.modules)
    start_rss = get_rss()
    start_time = time.time()

    exec(src)

    end_time = time.time()
    end_rss = get_rss()
    end_modules = set(sys.modules)

    return {
        'time_ms': (time_ms := round((end_time - start_time) * 1000., 6)),
        'time_ms_s': f'{time_ms:_}',
        'rss': (rss := (end_rss - start_rss)),
        'rss_s': f'{rss:_}',
        'modules': sorted(end_modules - start_modules),
    }


#


# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': 'py/execstat',
    'mod_name': __name__,
}}


def _main() -> None:
    if len(sys.argv) == 2:
        pre = None
        [src] = sys.argv[1:]
    elif len(sys.argv) == 3:
        [pre, src] = sys.argv[1:]
    else:
        raise Exception('Invalid arguments')

    payload = '\n'.join([
        inspect.getsource(_run),
        f'dct = _run({src!r}, pre={pre!r})',
        'import json',
        'print(json.dumps(dct))',
    ])

    out_json = subprocess.check_output([sys.executable, '-c', payload])

    dct = json.loads(out_json)

    print(json.dumps(dct, indent=2))


if __name__ == '__main__':
    _main()
