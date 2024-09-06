import dataclasses as dc

from .. import harness


def test_args():
    tys = set()
    print()
    for name, cls in harness.BOOTSTRAP_TYPES_BY_NAME.items():
        print(name)
        for f in dc.fields(cls.Config):
            print((f.name, f.type))
            tys.add(f.type)
        print()
    for ty in sorted(map(repr, tys)):
        print(ty)
    print()
