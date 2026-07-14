import pytest

from ...testing import pytest as ptu
from .. import crypto


@ptu.skip.if_cant_import('cryptography')
@pytest.mark.parametrize('sec', [
    crypto.FernetCrypto(),
    crypto.AesgcmCrypto(),
    crypto.Chacha20Poly1305Crypto(),
])
def test_crypto_crypto(sec: crypto.Crypto) -> None:
    key = sec.generate_key()

    raw = b'hi there'
    enc = sec.encrypt(raw, key)

    dec = sec.decrypt(enc, key)
    assert dec == raw

    with pytest.raises(crypto.DecryptionError):
        sec.decrypt(enc, bytes([key[0] + 1 if key[0] < 255 else 0]) + key[1:])
