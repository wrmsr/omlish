#include <iostream>

#include <pybind11/pybind11.h>
#include <tests/constructor_stats.h>

#include "pyrocksdb.h"


namespace py = pybind11;
using namespace std;

// class PySnapshot : public Snapshot {
// public:
//     using Snapshot::Snapshot;
//
//     SequenceNumber GetSequenceNumber() const override {
//         PYBIND11_OVERLOAD_PURE(
//                 SequenceNumber,
//                 rocksdb::Snapshot,
//                 GetSequenceNumber
//         );
//     }
// };


void init_snapshot(py::module& m) {
    // py::class_<Snapshot, PySnapshot, std::unique_ptr<Snapshot, py::nodelete>> snapshot(m, "Snapshot");
    // snapshot
    //     .def(py::init<>());

    // py::class_<Animal, PyAnimal [> <--- trampoline<]> animal(m, "Animal");
    // animal
    // .def(py::init<>())
    // .def("go", &Animal::go)
    // .def("vvv", &Animal::vvv);

    // py::class_<Dog>(m, "Dog", animal)
    // .def(py::init<>());

    // m.def("call_go", &call_go);
}


