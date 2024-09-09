cmake_minimum_required(VERSION 3.4...3.18)
project(python_rocksdb)

add_subdirectory(pybind11)

set(USE_RTTI ON)
add_subdirectory(rocksdb)

pybind11_add_module(
    pyrocksdb
    src/pyrocksdb/pyrocksdb.cc
    src/pyrocksdb/db.cc
    src/pyrocksdb/options.cc
    src/pyrocksdb/slice.cc
    src/pyrocksdb/status.cc
    src/pyrocksdb/write_batch.cc
    src/pyrocksdb/iterator.cc
    src/pyrocksdb/filter_policy.cc
    src/pyrocksdb/merge_operator.cc
    src/pyrocksdb/transaction_db.cc
    src/pyrocksdb/snapshot.cc
)

target_link_libraries(pyrocksdb PRIVATE rocksdb)
