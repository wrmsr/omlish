def latin1_decode(s: str) -> str:
    return s.encode('latin1').decode(errors='replace')


def latin1_encode(s: str) -> str:
    return s.encode().decode('latin1')
