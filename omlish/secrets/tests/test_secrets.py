from .. import secrets as sec


def test_logging():
    s = sec.LoggingSecrets(
        sec.MappingSecrets({'foo': 'bar'}),
    )
    assert s.get('foo') == 'bar'


def test_cache_ttl():
    cts: dict[str, int] = {}

    def f(k):
        cts[k] = cts.get(k, 0) + 1
        return k + '!'

    now = .0
    s = sec.CachingSecrets(
        sec.FnSecrets(f),
        ttl_s=1.,
        clock=lambda: now,
    )

    assert not cts
    assert s.get('a') == 'a!'
    assert cts['a'] == 1
    assert s.get('a') == 'a!'
    assert cts['a'] == 1
    now = .2
    assert s.get('b') == 'b!'
    assert cts['b'] == 1
    for t in [.5, .9]:
        now = t
        assert s.get('a') == 'a!'
        assert cts['a'] == 1
        assert s.get('b') == 'b!'
        assert cts['b'] == 1
    assert s.get('c') == 'c!'
    assert cts == {'a': 1, 'b': 1, 'c': 1}
    now = 1.
    assert s.get('a') == 'a!'
    assert cts['a'] == 2
    assert s.get('a') == 'a!'
    assert cts['a'] == 2
    assert s.get('b') == 'b!'
    assert cts['b'] == 1
    now = 1.89
    assert s.get('c') == 'c!'
    assert cts['c'] == 1
    assert s.get('b') == 'b!'
    assert cts['b'] == 2
    now = 1.9
    assert s.get('c') == 'c!'
    assert cts['c'] == 2
    assert s.get('b') == 'b!'
    assert cts['b'] == 2
    assert s.get('a') == 'a!'
    assert cts['a'] == 2
    now = 2.
    assert s.get('a') == 'a!'
    assert cts['a'] == 3
