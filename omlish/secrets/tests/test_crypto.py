import pytest

from ..crypto import Crypto
from ..crypto import OpensslSubprocessCrypto
from ..subprocesses import pipe_fd_subprocess_file_input
from ..subprocesses import temp_subprocess_file_input


@pytest.mark.parametrize('sec', [
    OpensslSubprocessCrypto(),
    OpensslSubprocessCrypto(file_input=temp_subprocess_file_input),  # noqa
    OpensslSubprocessCrypto(file_input=pipe_fd_subprocess_file_input),  # noqa
])
def test_crypto(sec: Crypto) -> None:
    key = sec.generate_key()
    print(repr(key))

    raw = b'hi there'
    enc = sec.encrypt(raw, key)
    print(repr(enc))

    dec = sec.decrypt(enc, key)
    print(repr(dec))
