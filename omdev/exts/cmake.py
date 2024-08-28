"""
TODO:
 - symlink headers, included src files (hamt_impl, ...)
 - point / copy output to dst dirs
 - libs
  - ..
   - pybind
   - catch2?
   - json? https://github.com/nlohmann/json
  - FindPackages? FetchContent? built_ext won't have that
  - move omml git / data retriever stuff into omdev, get just the one header file from git via sha?

==

Done:
 - https://intellij-support.jetbrains.com/hc/en-us/community/posts/206608485-Multiple-Jetbrain-IDE-sharing-the-same-project-directory really?
  - aight, generate a whole cmake subdir with symlinks to src files lol

"""  # noqa
import io
import logging
import os.path
import shutil
import sys
import sysconfig

from omlish import check
from omlish import logs

from .. import cmake


log = logging.getLogger(__name__)


def _main() -> None:
    logs.configure_standard_logging('INFO')

    prj_root = os.path.abspath(os.getcwd())
    if not os.path.isfile(os.path.join(prj_root, 'pyproject.toml')):
        raise Exception('Must be run in project root')

    cmake_dir = os.path.join(prj_root, 'cmake')
    if os.path.exists(cmake_dir):
        for e in os.listdir(cmake_dir):
            if e == '.idea':
                continue
            ep = os.path.join(cmake_dir, e)
            if os.path.isfile(ep):
                os.unlink(ep)
            else:
                shutil.rmtree(ep)
    else:
        os.mkdir(cmake_dir)

    with open(os.path.join(cmake_dir, '.gitignore'), 'w') as f:
        f.write('\n'.join(sorted(['/cmake-*', '/build'])))

    # idea_dir = os.path.join(cmake_dir, '.idea')
    # if not os.path.isdir(idea_dir):
    #     os.mkdir(idea_dir)
    # idea_name_file = os.path.join(idea_dir, '.name')
    # if not os.path.isfile(idea_name_file):
    #     with open(idea_name_file, 'w') as f:
    #         f.write('omlish')

    venv_exe = sys.executable
    venv_root = os.path.abspath(os.path.join(os.path.dirname(venv_exe), '..'))
    real_exe = os.path.realpath(venv_exe)
    py_root = os.path.abspath(os.path.join(os.path.dirname(real_exe), '..'))
    py_sfx = '.'.join(map(str, sys.version_info[:2]))

    out = io.StringIO()
    gen = cmake.CmakeGen(out)

    prj_name = 'omlish'
    var_prefix = prj_name.upper()

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
            *([[
                '-bundle',
                '"-undefined dynamic_lookup"',
            ]] if sys.platform == 'darwin' else []),
        ),
    ))

    for ext_src in [
        'omdev/exts/_boilerplate.cc',
        'x/dev/c/junk.cc',
        'x/dev/c/_uuid.cc',
        'x/dev/c/csv/_csvloader.cc',
    ]:
        ext_name = ext_src.rpartition('.')[0].replace('/', '__')

        log.info('Adding cmake c extension: %s -> %s', ext_src, ext_name)

        so_name = ''.join([
            os.path.basename(ext_src).split('.')[0],
            '.',
            sysconfig.get_config_var('SOABI'),
            sysconfig.get_config_var('SHLIB_SUFFIX'),
        ])

        sl = os.path.join(cmake_dir, ext_src)
        sal = os.path.abspath(sl)
        sd = os.path.dirname(sal)
        os.makedirs(sd, exist_ok=True)
        rp = os.path.relpath(os.path.abspath(ext_src), sd)
        os.symlink(rp, sal)

        gen.write_target(cmake.ModuleLibrary(
            ext_name,
            src_files=[
                sl,
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
            extra_cmds=[
                cmake.Command(
                    'add_custom_command',
                    ['TARGET', ext_name, 'POST_BUILD'],
                    [
                        ' '.join([
                            'COMMAND ${CMAKE_COMMAND} -E ',
                            f'copy $<TARGET_FILE_NAME:{ext_name}> ../../{os.path.dirname(ext_src)}/{so_name}',
                        ]),
                        'COMMAND_EXPAND_LISTS',
                    ],
                ),
            ],
        ))

    # print(out.getvalue())
    with open(os.path.join(cmake_dir, 'CMakeLists.txt'), 'w') as f:
        f.write(out.getvalue())


if __name__ == '__main__':
    _main()
