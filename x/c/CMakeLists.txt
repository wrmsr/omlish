cmake_minimum_required(VERSION 2.8.9)

project(junk)

add_library(junk MODULE
        junk.cc
)

target_include_directories(junk PUBLIC
        ../../.venv/include

        $ENV{HOME}/.pyenv/versions/3.11.8/include/python3.11

#        $ENV{HOME}/src/python/cpython
#        $ENV{HOME}/src/python/cpython/include
)

target_compile_options(junk PUBLIC
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
target_link_directories(junk PUBLIC
         $ENV{HOME}/.pyenv/versions/3.11.8/lib

#        $ENV{HOME}/src/python/cpython
)

target_link_libraries(junk
        -bundle
        "-undefined dynamic_lookup"
)