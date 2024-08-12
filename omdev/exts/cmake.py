"""
TODO:
 - https://intellij-support.jetbrains.com/hc/en-us/community/posts/206608485-Multiple-Jetbrain-IDE-sharing-the-same-project-directory really?
  - aight, generate a whole cmake subdir with symlinks to src files
"""  # noqa
import io
import os.path
import shutil
import sys

from omlish import check

from .. import cmake


def _main() -> None:
    # py_root = '$ENV{HOME}/.pyenv/versions/3.11.8/'

    prj_root = os.path.abspath(os.getcwd())
    if not os.path.isfile(os.path.join(prj_root, 'pyproject.toml')):
        raise Exception('Must be run in project root')

    cmake_dir = os.path.join(prj_root, 'cmake')
    if os.path.exists(cmake_dir):
        shutil.rmtree(cmake_dir)

    os.mkdir(cmake_dir)

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
            ['-std=c++20'],
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

    for ext_name, ext_srcs in [
        ('junk', ['x/dev/c/junk.cc']),
        ('_uuid', ['x/dev/c/_uuid.cc']),
    ]:
        src_links = []
        for sf in ext_srcs:
            sl = os.path.join(cmake_dir, sf)
            sal = os.path.abspath(sl)
            sd = os.path.dirname(sal)
            if not os.path.isdir(sd):
                os.makedirs(sd)
            rp = os.path.relpath(os.path.abspath(sf), sd)
            os.symlink(rp, sal)
            src_links.append(sl)

        gen.write_target(cmake.ModuleLibrary(
            ext_name,
            src_files=[
                *src_links,
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
    with open(os.path.join(cmake_dir, 'CMakeLists.txt'), 'w') as f:
        f.write(out.getvalue())


if __name__ == '__main__':
    _main()
