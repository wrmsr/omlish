"""
https://avro.apache.org/docs/1.11.1/specification/

https://lucene.apache.org/core/3_5_0/fileformats.html#VInt
https://protobuf.dev/programming-guides/encoding/#types
"""
import io
import os.path
import typing as ta

from omlish import check
from omlish.formats import json


def read_varint(data: ta.Iterator[int]) -> int:
    shift = 0
    result = 0
    for byte in data:
        result |= (byte & 0x7F) << shift
        shift += 7
        if not (byte & 0x80):
            break
    return result


def decode_zigzag(n: int) -> int:
    return (n >> 1) ^ -(n & 1)


def read_zigzag_varint(data: ta.Iterator[int]) -> int:
    varint_value = read_varint(data)
    return decode_zigzag(varint_value)


def _main():
    test_file = os.path.join(os.path.dirname(__file__), '.data', 'lineitem_iceberg', 'metadata', '10eaca8a-1e1c-421e-ad6d-b232e5ee23d3-m0.avro')  # noqa
    with open(test_file, 'rb') as f:
        buf = f.read()

    rdr = io.BytesIO(buf)
    hdr_magic = rdr.read(4)
    check.equal(hdr_magic, b'Obj\x01')

    bytes_it = iter(lambda: rdr.read(1), b'')
    ints_it = map(ord, bytes_it)

    # {"type": "map", "values": "bytes"}
    dct = {}
    num_items = read_zigzag_varint(ints_it)
    for i in range(num_items):
        k_len = read_zigzag_varint(ints_it)
        k = rdr.read(k_len)
        v_len = read_zigzag_varint(ints_it)
        v = rdr.read(v_len)
        dct[k] = v

    schema = json.loads(dct[b'schema'].decode('utf-8'))
    avro_schema = json.loads(dct[b'avro.schema'].decode('utf-8'))
    iceberg_schema = json.loads(dct[b'iceberg.schema'].decode('utf-8'))

    sync_marker = rdr.read(16)

    print(sync_marker)


if __name__ == '__main__':
    _main()
