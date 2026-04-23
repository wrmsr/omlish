from ...api.configs import ConfigRegistry
from ...api.contexts import MarshalFactoryContext
from ...singular.primitives import PRIMITIVE_MARSHALER_FACTORY
from ..api import LazyInit
from ..lazyinit import LazyInitRunningMarshalerFactory


def test_lazyinit():
    cfgs = ConfigRegistry()

    def foo(cfgs2):
        pass

    cfgs.update(None, LazyInit(foo))

    for _ in range(2):
        mf = LazyInitRunningMarshalerFactory(PRIMITIVE_MARSHALER_FACTORY)
        mfc = MarshalFactoryContext(configs=cfgs)
        mr = mf.make_marshaler(mfc, int)
        print(mr)
