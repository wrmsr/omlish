import pytest

from .. import crypto
from .. import openssl
from ..subprocesses import pipe_fd_subprocess_file_input
from ..subprocesses import temp_subprocess_file_input


@pytest.mark.parametrize('sec', [
    openssl.OpensslSubprocessAes256CbcCrypto(file_input=temp_subprocess_file_input),  # noqa
    openssl.OpensslSubprocessAes256CbcCrypto(file_input=pipe_fd_subprocess_file_input),  # noqa
])
def test_openssl_subproc_crypto(sec: crypto.Crypto) -> None:
    key = sec.generate_key()

    raw = b'hi there'
    enc = sec.encrypt(raw, key)

    dec = sec.decrypt(enc, key)
    assert dec == raw


@pytest.mark.parametrize('sec', [
    openssl.OpensslAes265CbcCrypto(),
])
def test_crypto_openssl(sec: crypto.Crypto) -> None:
    key = sec.generate_key()

    raw = b'hi there'
    enc = sec.encrypt(raw, key)

    dec = sec.decrypt(enc, key)
    assert dec == raw

    # NOTE: not aead/gcm - will happily decrypt garbage.
    # with pytest.raises(crypto.DecryptionError):
    #     dec = sec.decrypt(enc, bytes([key[0] + 1 if key[0] < 255 else 0]) + key[1:])  # noqa
