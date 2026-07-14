#!/usr/bin/env python3
"""
Some environments refuse to support running modules rather than scripts, so this is just "python -m" functionality
exposed as a script.
"""
import runpy
import sys


##


def _main() -> int:
    # Run the module specified as the next command line argument
    if len(sys.argv) < 2:
        print('No module specified for execution', file=sys.stderr)
        return 1

    if sys.argv[1] == '--wait':
        import os
        print(os.getpid())
        input()
        sys.argv.pop(1)

    del sys.argv[0]  # Make the requested module sys.argv[0]
    runpy._run_module_as_main(sys.argv[0])  # type: ignore  # noqa
    return 0


if __name__ == '__main__':
    sys.exit(_main())
