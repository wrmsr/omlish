SHELL:=/bin/bash

#

PYBIND11_URL=https://github.com/pybind/pybind11
PYBIND11_REV=v2.13.5

ROCKSDB_URL=https://github.com/facebook/rocksdb
ROCKSDB_REV=v9.6.1

#

.PHONY: pybind11
pybind11:
	git clone ${PYBIND11_URL}
	(cd pybind11 && git checkout ${PYBIND11_REV})

.PHONY: rocksdb
rocksdb:
	git clone ${ROCKSDB_URL}
	(cd rocksdb && git checkout ${ROCKSDB_REV})
