import re

from .exceptions import ProtocolError


NICKNAME_RE = re.compile(b'[a-zA-Z[\\]\\\\`_^{|}][a-zA-Z[\\]\\\\`_^{|}0-9-]{0,8}$')
CHANNEL_RE = re.compile(b'([#+&]|![A-Z0-9]{5})[^\x00\x0b\r\n ,:]+$')
HOSTMASK_RE = re.compile(b'(?:[^\x00?*]|[^\x00\\\\]\\?|\\*)+')


def validate_channel_name(name: bytes) -> bytes:
    """Ensure that a channel name conforms to the restrictions of RFC 2818."""

    if not CHANNEL_RE.match(name):
        raise ProtocolError(f'invalid channel name: {name.decode("ascii", errors="backslashreplace")}')
    return name


def validate_nickname(name: bytes) -> bytes:
    """Ensure that a nickname conforms to the restrictions of RFC 2818."""

    if not NICKNAME_RE.match(name):
        raise ProtocolError(f'invalid nickname: {name.decode("ascii", errors="backslashreplace")}')
    return name


def validate_hostmask(mask: bytes) -> bytes:
    """Ensure that a host mask conforms to the restrictions of RFC 2818."""

    if not HOSTMASK_RE.match(mask):
        raise ProtocolError(f'invalid host mask: {mask.decode("ascii", errors="backslashreplace")}')
    return mask


def match_hostmask(prefix: bytes, mask: bytes) -> bool:
    """Match a prefix against a hostmask."""

    prefix_index = mask_index = 0
    escape = False
    while prefix_index < len(prefix) and mask_index < len(mask):
        mask_char = mask[mask_index]
        prefix_char = prefix[prefix_index]
        if mask[mask_index] == b'\\':
            escape = True
            mask_index += 1
            mask_char = mask[mask_index]

        prefix_index += 1
        mask_index += 1
        if escape or mask_char not in b'?*':
            if mask_char != prefix_char:
                return False
        elif mask_char == b'?':
            pass
        elif mask_char == b'*':
            if mask_index < len(mask):
                mask_char = mask[mask_index]
                prefix_index = prefix.find(mask_char, prefix_index)
                if prefix_index == -1:
                    return False
            else:
                break

    return True
