"""
https://docs.python.org/3/library/site.html

https://github.com/xolox/python-coloredlogs/blob/65bdfe976ac0bf81e8c0bd9a98242b9d666b2859/setup.py#L64

_distutils_hack

runhack.pth: import x.runhack; x.runhack._run()

==

sys.argv=['/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py', '--multiprocess', '--qt-support=auto', '--client', '127.0.0.1', '--port', '64678', '--file', '/Users/spinlock/src/wrmsr/omlish/x/asts/marshal.py']
sys.orig_argv=['/Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python', '-X', 'pycache_prefix=/Users/spinlock/Library/Caches/JetBrains/PyCharm2024.2/cpython-cache', '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py', '--multiprocess', '--qt-support=auto', '--client', '127.0.0.1', '--port', '64678', '--file', '/Users/spinlock/src/wrmsr/omlish/x/asts/marshal.py']

sys.argv=['/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py', '--multiprocess', '--qt-support=auto', '--client', '127.0.0.1', '--port', '64687', '--file', '/Users/spinlock/src/wrmsr/omlish/x/dp/dp20240312_llamafs/lfs.py']
sys.orig_argv=['/Users/spinlock/.pyenv/versions/3.12.6/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python', '-X', 'pycache_prefix=/Users/spinlock/Library/Caches/JetBrains/PyCharm2024.2/cpython-cache', '/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py', '--multiprocess', '--qt-support=auto', '--client', '127.0.0.1', '--port', '64687', '--file', '/Users/spinlock/src/wrmsr/omlish/x/dp/dp20240312_llamafs/lfs.py']

"""
import os
import sys


_HAS_RUN = False


def _run() -> None:
    global _HAS_RUN
    if _HAS_RUN:
        return
    _HAS_RUN = True

    print(f'{sys.argv=}')
    print(f'{sys.orig_argv=}')
    print(f'{os.getcwd()}')

    # breakpoint()

    # sys.argv[-1] = 'print(2)'
