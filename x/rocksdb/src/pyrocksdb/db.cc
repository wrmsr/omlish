#include <pybind11/pybind11.h>

#include "pyrocksdb.h"

namespace py = pybind11;


void init_db(py::module& m) {
    py::class_<py_DB>(m, "DB")
        .def(py::init<>())
        .def(
            "open",
            (Status(py_DB::*)(const Options&, const std::string&)) &py_DB::Open,
            py::arg("options"),
            py::arg("name")
        )
        .def(
            "open",
            (py::tuple(py_DB::*)(const DBOptions&, const std::string&, const std::vector<ColumnFamilyDescriptor>&)) &py_DB::Open,
            py::arg("db_options"),
            py::arg("name"),
            py::arg("column_families")
        )
        .def(
            "open_for_readonly",
            (Status(py_DB::*)(const Options&, const std::string&, bool error_if_log_file_exist)) &py_DB::OpenForReadOnly,
            py::arg("options"),
            py::arg("name"),
            py::arg("error_if_log_file_exist") = false
        )
        .def(
            "open_for_readonly",
            (py::tuple(py_DB::*)(const DBOptions&, const std::string&, const std::vector<ColumnFamilyDescriptor>&, bool)) &py_DB::OpenForReadOnly,
            py::arg("db_options"),
            py::arg("name"),
            py::arg("column_families"),
            py::arg("error_if_log_file_exist") = false
        )
        .def("put", (Status(py_DB::*)(const WriteOptions&, ColumnFamilyHandle* , const std::string&, const std::string&)) &py_DB::Put)
        .def("put", (Status(py_DB::*)(const WriteOptions&, const std::string&, const std::string&)) &py_DB::Put)
        .def("write", &py_DB::Write)
        .def("get", (std::unique_ptr<Blob>(py_DB::*)(const ReadOptions&, const std::string&)) &py_DB::Get)
        .def("get", (std::unique_ptr<Blob>(py_DB::*)(const ReadOptions&, ColumnFamilyHandle* , const std::string&)) &py_DB::Get)
        .def("delete", (Status(py_DB::*)(const WriteOptions&, const std::string&)) &py_DB::Delete)
        .def("delete", (Status(py_DB::*)(const WriteOptions&, ColumnFamilyHandle* , const std::string&)) &py_DB::Delete)
        .def("compact_range", (Status(py_DB::*)(const CompactRangeOptions&, ColumnFamilyHandle*, const Slice*, const Slice*)) &py_DB::CompactRange)
        .def("compact_range", (Status(py_DB::*)(const CompactRangeOptions&, const Slice*, const Slice*)) &py_DB::CompactRange)
        .def("close", &py_DB::Close)
        .def("create_column_family", &py_DB::CreateColumnFamily)
        .def("iterator", (std::unique_ptr<IteratorWrapper>(py_DB::*)(const ReadOptions&)) &py_DB::NewIterator)
        .def("iterator", (std::unique_ptr<IteratorWrapper>(py_DB::*)(const ReadOptions&, ColumnFamilyHandle*)) &py_DB::NewIterator)
        // .def_readonly("DefaultColumnFamilyName", &rocksdb::kDefaultColumnFamilyName)
        ;

    m.attr("DefaultColumnFamilyName") = rocksdb::kDefaultColumnFamilyName;
}
