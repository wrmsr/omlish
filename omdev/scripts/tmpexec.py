#!/usr/bin/env python3
# @omlish-script
"""
TODO:
 - can xargs just do this lol
"""
import argparse
import os
import subprocess
import sys
import tempfile


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-I', '--replstr', default='%')
    parser.add_argument('-Q', '--stdout-silenced', action='store_true')
    parser.add_argument('-E', '--stdout-to-stderr', action='store_true')
    parser.add_argument('-c', '--cat', action='store_true')
    parser.add_argument('-k', '--keep', action='store_true')
    parser.add_argument('--read-size', type=int, default=0x4000)
    args, rest = parser.parse_known_args()

    fd, tmp_file = tempfile.mkstemp()
    os.close(fd)

    argv = [tmp_file if a == args.replstr else a for a in rest]

    kw: dict = {}
    if args.stdout_silenced:
        kw.update(stdout=open('/dev/null', 'wb'))  # noqa
    elif args.stdout_to_stderr:
        kw.update(stdout=sys.stderr)

    subprocess.check_call(argv, **kw)

    if args.cat:
        try:
            with open(tmp_file, 'rb') as f:
                while buf := f.read(args.read_size):
                    sys.stdout.buffer.write(buf)
        finally:
            if not args.keep:
                os.unlink(tmp_file)

    else:
        print(tmp_file)


# @omlish-manifest
_CLI_MODULE = {'!.cli.types.CliModule': {
    'name': 'tmpexec',
    'module': __name__,
}}


if __name__ == '__main__':
    _main()
