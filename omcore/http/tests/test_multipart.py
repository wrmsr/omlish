from ..multipart import MultipartEncoder
from ..multipart import MultipartField


def test_multipart():
    me = MultipartEncoder([
        MultipartField(
            b'abcd1234',
            b'image',
            b'foo.jpeg',
            headers=[(b'Content-Type', b'image/jpeg')],
        ),
    ], boundary=b'----WebKitFormBoundary7MA4YWxkTrZu0gW')

    assert me.content() == (
        b'------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n'
        b'Content-Disposition: form-data; name="image"; filename="foo.jpeg"\r\n'
        b'Content-Type: image/jpeg\r\n'
        b'\r\n'
        b'abcd1234\r\n'
        b'------WebKitFormBoundary7MA4YWxkTrZu0gW--\r\n'
    )
