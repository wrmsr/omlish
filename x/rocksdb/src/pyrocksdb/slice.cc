#include <iostream>

#include <pybind11/pybind11.h>

#include "pyrocksdb.h"

namespace py = pybind11;


void init_slice(py::module& m) {
    py::class_<Slice>(m, "Slice")
        .def(py::init<const std::string&>());
}
