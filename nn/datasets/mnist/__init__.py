import gzip
import pathlib

import numpy as np

from ...tensor import Tensor


def fetch_mnist(tensors=False):
    def parse(file):
        return np.frombuffer(gzip.open(file).read(), dtype=np.uint8).copy()

    dirname = pathlib.Path(__file__).parent.resolve()

    X_train = parse(dirname / "train-images-idx3-ubyte.gz")[0x10:].reshape((-1, 28*28)).astype(np.float32)
    Y_train = parse(dirname / "train-labels-idx1-ubyte.gz")[8:]
    X_test = parse(dirname / "t10k-images-idx3-ubyte.gz")[0x10:].reshape((-1, 28*28)).astype(np.float32)
    Y_test = parse(dirname / "t10k-labels-idx1-ubyte.gz")[8:]

    if tensors:
        return (
            Tensor(X_train).reshape(-1, 1, 28, 28),
            Tensor(Y_train),
            Tensor(X_test).reshape(-1, 1, 28, 28),
            Tensor(Y_test),
        )
    else:
        return X_train, Y_train, X_test, Y_test
