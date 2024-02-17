/*
https://github.com/pybind/cmake_example

/Library/Developer/CommandLineTools/usr/bin/c++
  -DVERSION_INFO=""
  -Dcmake_example_EXPORTS
  -isystem /Users/spinlock/src/pybind/cmake_example/pybind11/include
  -isystem /Users/spinlock/.pyenv/versions/3.10.12/include/python3.10
  -std=gnu++11
  -arch arm64
  -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX13.1.sdk
  -mmacosx-version-min=12.6
  -fPIC
  -fvisibility=hidden
  -flto
  -MD
  -MT CMakeFiles/cmake_example.dir/src/main.cpp.o
  -MF CMakeFiles/cmake_example.dir/src/main.cpp.o.d
  -o CMakeFiles/cmake_example.dir/src/main.cpp.o
  -c /Users/spinlock/src/pybind/cmake_example/src/main.cpp

/Library/Developer/CommandLineTools/usr/bin/c++
  -arch arm64
  -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX13.1.sdk
  -mmacosx-version-min=12.6
  -bundle
  -Wl,-headerpad_max_install_names
  -Xlinker
  -undefined
  -Xlinker dynamic_lookup
  -flto
  -o cmake_example.cpython-310-darwin.so
  CMakeFiles/cmake_example.dir/src/main.cpp.o
*/
#include <pybind11/pybind11.h>

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

int add(int i, int j) {
    return i + j;
}

namespace py = pybind11;

PYBIND11_MODULE(cmake_example, m) {
    m.doc() = R"pbdoc(
        Pybind11 example plugin
        -----------------------

        .. currentmodule:: cmake_example

        .. autosummary::
           :toctree: _generate

           add
           subtract
    )pbdoc";

    m.def("add", &add, R"pbdoc(
        Add two numbers

        Some other explanation about the add function.
    )pbdoc");

    m.def("subtract", [](int i, int j) { return i - j; }, R"pbdoc(
        Subtract two numbers

        Some other explanation about the subtract function.
    )pbdoc");

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}
