from .. import secrets as sec


def test_logging():
    s = sec.LoggingSecrets(
        sec.MappingSecrets({'foo': 'bar'}),
    )
    assert s.get('foo') == 'bar'


def test_cache_ttl():
    cts = {}

    def f(k):
        cts[k] = cts.get(k, 0) + 1
        return k + '!'

    now = 0.
    s = sec.CachingSecrets(
        sec.FnSecrets(f),
        ttl_s=1.,
        clock=lambda: now,
    )

    assert not cts
    
