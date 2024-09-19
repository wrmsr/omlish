import struct


def isclose(a: float, b: float, *, rel_tol: float = 1e-09, abs_tol: float = 0.0) -> float:
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def float_to_bytes(f: float) -> bytes:
    return struct.pack('>f', f)


def bytes_to_float(b: bytes) -> float:
    return struct.unpack('>f', b)[0]
