"""
TODO:
 - cython
 - zigzag
 - memoryview
 - signedness
 - protobuf

http://www.amazontechon.com/locale/ro/pdfs/0_3_Integer%20encodings_new%20template.pdf
https://github.com/stoklund/varint
https://github.com/dermesser/integer-encoding-rs/blob/master/src/varint.rs
https://github.com/apache/lucene-solr/blob/e2521b2a8baabdaf43b92192588f51e042d21e97/lucene/core/src/java/org/apache/lucene/store/DataOutput.java#L186
https://github.com/apache/lucene-solr/blob/e2521b2a8baabdaf43b92192588f51e042d21e97/lucene/core/src/java/org/apache/lucene/store/DataInput.java#L113
"""
import typing as ta

from . import lang


lang.warn_unstable()


def encode_iter(is_: ta.Iterator[int], b: bytearray):
    append = b.append
    for i in is_:
        if i < 0:
            raise ValueError(i)
        mask = ~0x7F
        while i & mask:
            append((i & 0x7F) | 0x80)
            i >>= 7
        append(i)
    return b


def decode_iter(bs: ta.Iterator[int]) -> ta.Iterator[int]:
    next_ = next
    while True:
        try:
            b = next_(bs)
        except StopIteration:
            return
        i = b & 0x7F
        shift = 7
        while b & 0x80:
            b = next_(bs)
            i |= (b & 0x7F) << shift
            shift += 7
        yield i


def encode(i: int) -> bytes:
    return bytes(encode_iter(iter([i]), bytearray()))


def decode(b: bytes) -> int:
    bs = iter(b)
    [i] = decode_iter(bs)
    try:
        next(bs)
    except StopIteration:
        pass
    else:
        raise ValueError(b)
    return i
