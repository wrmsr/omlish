from .. import secrets as sec


def test_logging():
    s = sec.LoggingSecrets(
        sec.SimpleSecrets({'foo': 'bar'}),
    )
    assert s.get('foo') == 'bar'
