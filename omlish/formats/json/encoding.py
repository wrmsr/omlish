import json


detect_encoding = json.detect_encoding


def decodes(s: str | bytes | bytearray) -> str:
    if isinstance(s, str):
        if s.startswith('\ufeff'):
            raise json.JSONDecodeError('Unexpected UTF-8 BOM (decode using utf-8-sig)', s, 0)
        return s

    elif isinstance(s, (bytes, bytearray)):
        return s.decode(detect_encoding(s), 'surrogatepass')

    else:
        raise TypeError(f'the JSON object must be str, bytes or bytearray, not {s.__class__.__name__}')
