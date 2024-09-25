#!/usr/bin/env python3
"""
TODO:
 - usable as 'curl -LsSf https://raw.githubusercontent.com/wrmsr/omlish/master/x/cli_install.py | python3'
 - used for self-reinstall, preserving non-root dists

==

if uv --version 2>/dev/null ; then \
    MGR="uv tool" ; \
    INST="install --refresh --prerelease=allow --python=${INSTALL_PYTHON_VERSION}"; \
    INJ="--with" ; \
else \
    MGR="pipx" ; \
    INST="install"; \
    INJ="--preinstall" ; \
fi ; \
\
CMD="$$MGR uninstall omdev-cli || true ; $$MGR $$INST omdev-cli" ; \
for D in ${INSTALL_EXTRAS} ; do \
    CMD+=" $$INJ $$D" ; \
done ; \
${SHELL} -c "$$CMD"
"""
import argparse
import itertools
import subprocess
import sys


DEFAULT_CLI_PKG = 'omdev-cli'
DEFAULT_PY_VERSION = '3.12'


def _main() -> None:
    if sys.version_info < (3, 8):
        raise RuntimeError(f'Unsupported python version: {sys.version_info}')

    parser = argparse.ArgumentParser()
    parser.add_argument('--cli', default=DEFAULT_CLI_PKG)
    parser.add_argument('--py', default=DEFAULT_PY_VERSION)
    parser.add_argument('extra', nargs='*')
    args = parser.parse_args()

    subprocess.check_call(['uv', '--version'])

    cli = args.cli
    if not cli:
        raise ValueError(f'Must specify cli')
    py = args.py
    if not py:
        raise ValueError(f'Must specify py')

    out = subprocess.check_output(['uv', 'tool', 'list']).decode()
    inst = {
        s.partition(' ')[0]
        for l in out.splitlines()
        if (s := l.strip())
        and not s.startswith('-')
    }
    if cli in inst:
        subprocess.check_call([
            'uv', 'tool',
            'uninstall', cli,
        ])

    subprocess.run([
        'uv', 'tool',
        'install',
        '--refresh',
        '--prerelease=allow',
        f'--python={py}',
        cli,
        *itertools.chain.from_iterable(['--with', e] for e in args.extra),
    ])


if __name__ == '__main__':
    _main()
