import io

from .. import cmake


##


EXT_TEMPLATE = """

##

add_library({name} MODULE
        {name}.cc
)

target_include_directories({name} PUBLIC ${{var_pfx}_INCLUDE_DIRECTORIES})
target_compile_options({name} PUBLIC ${{var_pfx}_COMPILE_OPTIONS})
target_link_directories({name} PUBLIC ${{var_pfx}_LINK_DIRECTORIES})
target_link_libraries({name} ${{var_pfx}_LINK_LIBRARIES})
"""  # noqa


##


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

    print(out.getvalue())


if __name__ == '__main__':
    _main()
