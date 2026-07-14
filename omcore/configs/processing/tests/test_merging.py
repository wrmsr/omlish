from ..merging import merge_configs


def test_merge_configs():
    assert merge_configs(
        {'a': 'a!', 'b': 'b!'},
        {'c': 'c!'},
        {'d': 'd!'},
    ) == {'a': 'a!', 'b': 'b!', 'c': 'c!', 'd': 'd!'}

    assert merge_configs(
        {'a': 'a!', 'b': 'b!'},
        {'c': 'c!'},
        {'a': 'a!!'},
    ) == {'a': 'a!!', 'b': 'b!', 'c': 'c!'}

    assert merge_configs(
        {'a': {'b': 'b!'}},
        {'c': 'c!'},
        {'a': 'a!!'},
    ) == {'a': 'a!!', 'c': 'c!'}

    assert merge_configs(
        {'a': {'b': 'b!'}},
        {'a': {'c': 'c!'}},
        {'d': 'd!'},
    ) == {'a': {'b': 'b!', 'c': 'c!'}, 'd': 'd!'}

    assert merge_configs(
        {'a': {'b': 'b!'}},
        {'a': {'c': 'c!'}},
        {'a': {'b': 'e!'}},
        {'d': 'd!'},
    ) == {'a': {'b': 'e!', 'c': 'c!'}, 'd': 'd!'}
