from .. import inject as inj


def test_inject():
    bs = [
        inj.Binding(inj.Key(int), inj.SimpleProvider(int, lambda: 420)),
    ]

