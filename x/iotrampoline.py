"""
TODO:
 - greenlets
"""
import os.path
import typing as ta


# Unlike regular files, empty bytes does not mean eof - None does.
IncrementalReader: ta.TypeAlias = ta.Callable[[bytes], bytes | None]


def nop_incremental_reader(data: bytes | None) -> bytes | None:
    return data


def _main() -> None:
    inc_rdr = nop_incremental_reader

    in_file = os.path.expanduser('~/Downloads/access.json.gz')
    with open(in_file, 'rb') as f:
        while data := f.read(0x1000):
            print(inc_rdr(data))
    print(inc_rdr(None))


if __name__ == '__main__':
    _main()
