"""
cmd = {list: 4} ['/Users/spinlock/src/wrmsr/omlish/.venv/bin/python', '/Users/spinlock/src/wrmsr/omlish/.venv/lib/python3.11/site-packages/pyproject_hooks/_in_process/_in_process.py', 'build_sdist', '/var/folders/0s/szmw_2x17m507jfhwyrkd65r0000gn/T/tmpm99i1fvx']
 0 = {str} '/Users/spinlock/src/wrmsr/omlish/.venv/bin/python'
 1 = {str} '/Users/spinlock/src/wrmsr/omlish/.venv/lib/python3.11/site-packages/pyproject_hooks/_in_process/_in_process.py'
 2 = {str} 'build_sdist'
 3 = {str} '/var/folders/0s/szmw_2x17m507jfhwyrkd65r0000gn/T/tmpm99i1fvx'
 __len__ = {int} 4
cwd = {str} '/Users/spinlock/src/wrmsr/omlish'
extra_environ = {dict: 1} {'_PYPROJECT_HOOKS_BUILD_BACKEND': 'setuptools.build_meta'}
"""
import json
import os.path
import shutil
import sys

from pyproject_hooks._in_process import _in_process as ip  # noqa


def _main():
    tmp_dir = os.path.abspath('tmp')
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)

    os.environ.update({
        '_PYPROJECT_HOOKS_BUILD_BACKEND': 'setuptools.build_meta',
    })

    with open(os.path.join(tmp_dir, 'input.json'), 'w') as f:
        f.write(json.dumps({
            'kwargs': {
                'config_settings': {},
                'sdist_directory': os.path.abspath('dist'),
            },
        }))

    sys.argv.extend(['build_sdist', tmp_dir])
    ip.main()


if __name__ == '__main__':
    _main()
