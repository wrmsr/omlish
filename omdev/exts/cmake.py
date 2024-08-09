BASE_TEMPLATE = """
cmake_minimum_required(VERSION 2.8.9)

project({prj_name})

##

set({var_pfx}_INCLUDE_DIRECTORIES
        ../../.venv/include

        $ENV{HOME}/.pyenv/versions/3.11.8/include/python3.11

        # $ENV{HOME}/src/python/cpython
        # $ENV{HOME}/src/python/cpython/include
)

set({var_pfx}_COMPILE_OPTIONS
        -Wsign-compare
        -Wunreachable-code
        -DNDEBUG
        -g
        -fwrapv
        -O3
        -Wall

        -g
        -c

        -std=c++14
)

set({var_pfx}_LINK_DIRECTORIES
        $ENV{HOME}/.pyenv/versions/3.11.8/lib

        # $ENV{HOME}/src/python/cpython
)

set({var_pfx}_LINK_LIBRARIES
        -bundle
        "-undefined dynamic_lookup"
)
"""  # noqa


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


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
