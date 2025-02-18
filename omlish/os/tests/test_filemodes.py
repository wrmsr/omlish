from ..filemodes import FileMode


def test_file_modes():
    for ms in [
        'w+b',
        'ab',
        'a+b',
        'xb',
        'x+b',
        'wb',
        'w+b',
        'rb',
        'r+b',
    ]:
        fm0 = FileMode.parse(ms)
        print(fm0)
        rs0 = fm0.render()
        print(rs0)
        assert rs0 == ms

        fl0 = fm0.flags()
        print(fl0)
        fm1 = FileMode.from_flags(fl0)
        print(fm1)
        assert fm1 == fm0

        print()
