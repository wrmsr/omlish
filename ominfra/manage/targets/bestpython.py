import io

from omlish.lite.cached import cached_nullary
from omlish.lite.resources import read_package_resource_text


##


BEST_PYTHON_SH = read_package_resource_text(__package__, 'bestpython.sh')


@cached_nullary
def get_best_python_sh() -> str:
    buf = io.StringIO()

    for l in BEST_PYTHON_SH.strip().splitlines():
        if not (l := l.strip()):
            continue

        buf.write(l)

        if l.split()[-1] not in ('do', 'then', 'else'):
            buf.write(';')

        buf.write(' ')

    return buf.getvalue().strip(' ;')


if __name__ == '__main__':
    print(__import__('shlex').quote(get_best_python_sh()))
