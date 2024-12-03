import gzip


def test_gzip_inc():
    dec_data = b'foobar' * 128
    enc_data = gzip.compress(dec_data)
    print(enc_data)
