#include <pybind11/pybind11.h>

#include "pyrocksdb.h"

namespace py = pybind11;


class PyWriteBatch : public WriteBatch {

public:
    Status Put(const std::string &key, const std::string &value) {
        return WriteBatch::Put(nullptr, key, value);
    }

    Status Put(ColumnFamilyHandle *column_family, const std::string &key, const std::string &value) {
        return WriteBatch::Put(column_family, key, value);
    }

    Status Delete(const std::string &key) {
        return WriteBatch::Delete(nullptr, key);
    }

    Status Delete(ColumnFamilyHandle *column_family, const std::string &key) {
        return WriteBatch::Delete(column_family, key);
    }

    Status Merge(const std::string &key, const std::string &value) {
        return WriteBatch::Merge(nullptr, key, value);
    }
};

void init_write_batch(py::module &m) {
    py::class_<WriteBatch>(m, "_WriteBatch");
    py::class_<PyWriteBatch, WriteBatch>(m, "WriteBatch")
        .def(py::init<>())
        .def("put", (Status(PyWriteBatch::*)(const std::string&, const std::string&)) &PyWriteBatch::Put)
        .def("put", (Status(PyWriteBatch::*)(ColumnFamilyHandle *, const std::string&, const std::string&)) &PyWriteBatch::Put)
        .def("delete", (Status(PyWriteBatch::*)(const std::string&)) &PyWriteBatch::Delete)
        .def("delete", (Status(PyWriteBatch::*)(ColumnFamilyHandle *, const std::string&)) &PyWriteBatch::Delete);
        // .def("merge", &PyWriteBatch::Merge);
}
