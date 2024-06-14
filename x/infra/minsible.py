from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


class Play(dc.Frozen, lang.Abstract):
    pass


class File(Play, lang.Final):
    pass


class Stat(Play, lang.Final):
    pass


def _main():
    import omlish.marshal.factories  # noqa
    mf: msh.MarshalerFactory = msh.factories.TypeCacheFactory(
        msh.base.RecursiveMarshalerFactory(
            msh.factories.CompositeFactory(
                msh.polymorphism.PolymorphismMarshalerFactory(msh.polymorphism_from_subclasses(Play)),
                *msh.STANDARD_MARSHALER_FACTORIES,
            )
        )
    )


if __name__ == '__main__':
    _main()
