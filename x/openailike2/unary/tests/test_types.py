from ..requests import Request
from ...requests import UserRequestMessage


def test_types():
    req = Request(
        model='foo',
        messages=[
            UserRequestMessage(content='hi'),
        ],
    )

    print(req)
