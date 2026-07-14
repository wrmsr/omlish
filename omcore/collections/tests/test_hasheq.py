from ..hasheq import HashEqMap
from ..hasheq import hash_eq


def test_hash_eq_map():
    m: HashEqMap[int, int] = HashEqMap(
        hash_eq[int](
            lambda k: k % 3,
            lambda l, r: l == r,
        ),
        [
            (0, 10),
            (11, 20),
            (12, 21),
            (13, 22),
            (14, 23),
            (15, 24),
            (16, 25),
            (20, 30),
        ],
    )

    print(m)

    assert m[12] == 21

    for k in [12, 13, 14]:
        del m[k]

    assert (11, 20) in m.items()
    assert (11, 21) not in m.items()

    assert sorted(m.items()) == [
        (0, 10),
        (11, 20),
        (15, 24),
        (16, 25),
        (20, 30),
    ]

    assert sorted(m.values()) == [
        10,
        20,
        24,
        25,
        30,
    ]
