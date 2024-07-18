cmake_minimum_required(VERSION 2.8.9)

project(_tpch)

##

set(TPCH_INCLUDE_DIRECTORIES
        ../../.venv/include

        $ENV{HOME}/.pyenv/versions/3.11.8/include/python3.11

        # $ENV{HOME}/src/python/cpython
        # $ENV{HOME}/src/python/cpython/include
)

set(TPCH_COMPILE_OPTIONS
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

set(TPCH_LINK_DIRECTORIES
        $ENV{HOME}/.pyenv/versions/3.11.8/lib

        # $ENV{HOME}/src/python/cpython
)

set(TPCH_LINK_LIBRARIES
        -bundle
        "-undefined dynamic_lookup"
)

##

add_library(_tpch MODULE
        _tpch.cc
)

target_include_directories(_tpch PUBLIC ${TPCH_INCLUDE_DIRECTORIES})
target_compile_options(_tpch PUBLIC ${TPCH_COMPILE_OPTIONS})
target_link_directories(_tpch PUBLIC ${TPCH_LINK_DIRECTORIES})
target_link_libraries(_tpch ${TPCH_LINK_LIBRARIES})
