import io

from .. import cmake


def _main() -> None:
    out = io.StringIO()
    gen = cmake.CmakeGen(out)

    prj_name = 'junk'
    var_prefix = 'JUNK'

    gen.write(gen.preamble)
    gen.write('')

    gen.write(f'project({prj_name})')
    gen.write('')

    gen.write_var(cmake.Var(
        f'{var_prefix}_INCLUDE_DIRECTORIES',
        [
            '../../.venv/include',

            '',

            '$ENV{HOME}/.pyenv/versions/3.11.8/include/python3.11',

            # $ENV{HOME}/src/python/cpython
            # $ENV{HOME}/src/python/cpython/include
        ],
    ))

    gen.write_var(cmake.Var(
        f'{var_prefix}_COMPILE_OPTIONS',
        [
            '-Wsign-compare',
            '-Wunreachable-code',
            '-DNDEBUG',
            '-g',
            '-fwrapv',
            '-O3',
            '-Wall',

            '',

            '-g',
            '-c',

            '',

            '-std=c++17',
        ],
    ))

    gen.write_var(cmake.Var(
        f'{var_prefix}_LINK_DIRECTORIES',
        [
            '$ENV{HOME}/.pyenv/versions/3.11.8/lib',

            # $ENV{HOME}/src/python/cpython
        ],
    ))

    gen.write_var(cmake.Var(
        f'{var_prefix}_LINK_LIBRARIES',
        [
            '-bundle',
            '"-undefined dynamic_lookup"',
        ],
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
