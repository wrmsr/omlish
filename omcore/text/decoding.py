"""
TODO:
 - cext
"""
import array
import codecs
import typing as ta


##


def decode_to_list(
        raw: bytes,
        encoding: str = 'utf-8',
        *,
        errors: str = 'strict',
) -> list[str]:
    dec = codecs.getincrementaldecoder(encoding)(errors)
    end = len(raw) - 1
    return [dec.decode(bytes([b]), final=i == end) for i, b in enumerate(raw)]


#


class DecodedStringIndex(ta.NamedTuple):
    byte_offsets: ta.Sequence[int]


def decode_indexed(
        raw: bytes,
        encoding: str = 'utf-8',
        *,
        errors: str = 'strict',
) -> tuple[str, DecodedStringIndex]:
    dec_lst = decode_to_list(
        raw,
        encoding,
        errors=errors,
    )

    dec_s = ''.join(dec_lst)

    bo_arr_len = len(dec_s) + 1
    if bo_arr_len < 2**8:
        fmt = 'B'
    elif bo_arr_len < 2**16:
        fmt = 'H'
    elif bo_arr_len < 2**32:
        fmt = 'L'
    else:
        fmt = 'Q'

    bo_arr = array.array(fmt, [0]) * bo_arr_len
    so = 0
    lbo = 0
    for bo, s in enumerate(dec_lst):
        if s:
            bo_arr[so] = lbo
            so += 1
            lbo = bo + 1

    if so != len(dec_s):
        raise RuntimeError

    bo_arr[len(dec_s)] = len(raw)

    dsi = DecodedStringIndex(
        bo_arr,
    )

    return (dec_s, dsi)
