cmake_minimum_required(VERSION 2.8.9)

project(junk)

##

set(JUNK_INCLUDE_DIRECTORIES
        ../../.venv/include

        $ENV{HOME}/.pyenv/versions/3.11.8/include/python3.11

        # $ENV{HOME}/src/python/cpython
        # $ENV{HOME}/src/python/cpython/include
)

set(JUNK_COMPILE_OPTIONS
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

set(JUNK_LINK_DIRECTORIES
        $ENV{HOME}/.pyenv/versions/3.11.8/lib

        # $ENV{HOME}/src/python/cpython
)

set(JUNK_LINK_LIBRARIES
        -bundle
        "-undefined dynamic_lookup"
)

##

add_library(junk MODULE
        junk.cc
)

target_include_directories(junk PUBLIC ${JUNK_INCLUDE_DIRECTORIES})
target_compile_options(junk PUBLIC ${JUNK_COMPILE_OPTIONS})
target_link_directories(junk PUBLIC ${JUNK_LINK_DIRECTORIES})
target_link_libraries(junk ${JUNK_LINK_LIBRARIES})

##

add_library(_dispatch MODULE
        _dispatch.cc
)

target_include_directories(_dispatch PUBLIC ${JUNK_INCLUDE_DIRECTORIES})
target_compile_options(_dispatch PUBLIC ${JUNK_COMPILE_OPTIONS})
target_link_directories(_dispatch PUBLIC ${JUNK_LINK_DIRECTORIES})
target_link_libraries(_dispatch ${JUNK_LINK_LIBRARIES})
