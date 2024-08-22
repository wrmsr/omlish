import pytest

from .. import crypto
from ..subprocesses import pipe_fd_subprocess_file_input
from ..subprocesses import temp_subprocess_file_input


@pytest.mark.parametrize('sec', [
    crypto.OpensslSubprocessCrypto(),
    # crypto.OpensslSubprocessCrypto(file_input=temp_subprocess_file_input),  # noqa
    crypto.OpensslSubprocessCrypto(file_input=pipe_fd_subprocess_file_input),  # noqa
])
def test_openssl_subproc_crypto(sec: crypto.Crypto) -> None:
    key = sec.generate_key()

    raw = b'hi there'
    enc = sec.encrypt(raw, key)

    dec = sec.decrypt(enc, key)
    assert dec == raw


@pytest.mark.parametrize('sec', [
    crypto.FernetCrypto(),
    crypto.AesgsmCrypto(),
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
