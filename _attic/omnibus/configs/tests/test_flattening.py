from .. import flattening as flattening_


def test_flattening():
    m = {
        'a': 1,
        'b': {
            'c': 2
        },
        'd': [
            'e',
            {
                'f': 3
            }
        ],
        'g': [
            [
                'a',
                'b'
            ],
            [
                'c',
                'd'
            ]
        ]
    }
    for f in [flattening_.Flattening(), flattening_.Flattening(index_open='((', index_close='))')]:
        fl = f.flatten(m)
        ufl = f.unflatten(fl)
        assert ufl == m
