import pytest

from .. import crypto
from ..subprocesses import pipe_fd_subprocess_file_input
from ..subprocesses import temp_subprocess_file_input


@pytest.mark.parametrize('sec', [
    crypto.OpensslSubprocessCrypto(file_input=temp_subprocess_file_input),  # noqa
    crypto.OpensslSubprocessCrypto(file_input=pipe_fd_subprocess_file_input),  # noqa
])
def test_openssl_subproc_crypto(sec: crypto.Crypto) -> None:
    key = sec.generate_key()

    raw = b'hi there'
    enc = sec.encrypt(raw, key)

    ##

    # import hashlib
    # block_size = 16
    # key_length = 32
    # iv_length = 16
    # salt = enc[len('Salted__'):block_size]
    # dk = hashlib.pbkdf2_hmac('sha512', key, salt, 10_000, key_length + iv_length)

    # # def derive_key_and_iv(password, salt, key_length, iv_length):
    # #     d = d_i = ''
    # #     while len(d) < key_length + iv_length:
    # #         d_i = md5(d_i + password + salt).digest()
    # #         d += d_i
    # #     return , dk[key_length:key_length + iv_length]

    # # key, iv = derive_key_and_iv(password, salt, key_length, bs)
    # # cipher = AES.new(key, AES.MODE_CBC, iv)
    # # next_chunk = ''
    # # finished = False
    # # while not finished:
    # #     chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
    # #     if len(next_chunk) == 0:
    # #         padding_length = ord(chunk[-1])
    # #         chunk = chunk[:-padding_length]
    # #         finished = True
    # #     out_file.write(chunk)

    # from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    # cipher = Cipher(algorithms.AES256(dk[:key_length]), modes.CBC(dk[key_length:key_length + iv_length]))
    # decryptor = cipher.decryptor()
    # dec2 = decryptor.update(enc[16:]) + decryptor.finalize()
    # print(dec2)

    ##

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
