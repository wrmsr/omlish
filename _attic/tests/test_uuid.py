import uuid

from .. import uuid as uuid_


def test_uuid():
    s = '37b96676-18ff-4642-b818-a5b0f85cceef'

    for i in range(1, 5):
        assert uuid.UUID(s, version=i) == uuid_.new(s, version=i)
