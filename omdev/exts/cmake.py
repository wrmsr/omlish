import io
import os.path
import sys

from omlish import check

from .. import cmake


def _main() -> None:
    # py_root = '$ENV{HOME}/.pyenv/versions/3.11.8/'

    venv_exe = sys.executable
    venv_root = os.path.abspath(os.path.join(os.path.dirname(venv_exe), '..'))
    real_exe = os.path.realpath(venv_exe)
    py_root = os.path.abspath(os.path.join(os.path.dirname(real_exe), '..'))
    py_sfx = '.'.join(map(str, sys.version_info[:2]))

    out = io.StringIO()
    gen = cmake.CmakeGen(out)

    prj_name = 'junk'
    var_prefix = 'JUNK'

    gen.write(gen.preamble)
    gen.write('')

    gen.write(f'project({prj_name})')
    gen.write('')

    def sep_grps(*ls):
        # itertools.interleave? or smth?
        o = []
        for i, l in enumerate(ls):
            if not l:
                continue
            if i:
                o.append('')
            o.extend(check.not_isinstance(l, str))
        return o

    gen.write_var(cmake.Var(
        f'{var_prefix}_INCLUDE_DIRECTORIES',
        sep_grps(
            [f'{venv_root}/include'],
            [f'{py_root}/include/python{py_sfx}'],
            [
                # $ENV{HOME}/src/python/cpython
                # $ENV{HOME}/src/python/cpython/include
            ],
        ),
    ))

    gen.write_var(cmake.Var(
        f'{var_prefix}_COMPILE_OPTIONS',
        sep_grps(
            [
                '-Wsign-compare',
                '-Wunreachable-code',
                '-DNDEBUG',
                '-g',
                '-fwrapv',
                '-O3',
                '-Wall',
            ],
            [
                '-g',
                '-c',
            ],
            ['-std=c++17'],
        ),
    ))

    gen.write_var(cmake.Var(
        f'{var_prefix}_LINK_DIRECTORIES',
        sep_grps(
            [f'{py_root}/lib'],
            # ['$ENV{HOME}/src/python/cpython'],
        ),
    ))

    gen.write_var(cmake.Var(
        f'{var_prefix}_LINK_LIBRARIES',
        sep_grps(
            [
                '-bundle',
                '"-undefined dynamic_lookup"',
            ],
        ),
    ))

    for ext_name in [
        'junk',
        'foo',
    ]:
        gen.write_target(cmake.ModuleLibrary(
            ext_name,
            src_files=[
                f'{ext_name}.cc',
            ],
            include_dirs=[
                f'${{{var_prefix}_INCLUDE_DIRECTORIES}}',
            ],
            compile_opts=[
                f'${{{var_prefix}_COMPILE_OPTIONS}}',
            ],
            link_dirs=[
                f'${{{var_prefix}_LINK_DIRECTORIES}}',
            ],
            link_libs=[
                f'${{{var_prefix}_LINK_LIBRARIES}}',
            ],
        ))

    print(out.getvalue())


if __name__ == '__main__':
    _main()
