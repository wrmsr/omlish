import ctypes as ct


class iovec(ct.Structure):
    pass


iovec._fields_ = [
    ('iov_base', ct.c_void_p),  # Pointer to data.
    ('iov_len', ct.c_size_t),  # Length of data.
]


def _main():
    pass


if __name__ == '__main__':
    _main()
