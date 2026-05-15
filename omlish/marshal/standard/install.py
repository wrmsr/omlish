from ..api.configs import ConfigRegistry
from ..api.types import MarshalerFactory
from ..api.types import UnmarshalerFactory
from .defaults import DEFAULT_STANDARD_FACTORIES
from .factories import StandardMarshalerFactories
from .factories import StandardUnmarshalerFactories


##


def install_standard_factories(
        cfgs: ConfigRegistry,
        *factories: MarshalerFactory | UnmarshalerFactory,
) -> None:
    with cfgs._lock:  # noqa
        m_cfg = cfgs.get().get(StandardMarshalerFactories)
        u_cfg = cfgs.get().get(StandardUnmarshalerFactories)

        m_lst: list[MarshalerFactory] = list(
            m_cfg.lst if m_cfg is not None else DEFAULT_STANDARD_FACTORIES.marshaler_factories,
        )
        u_lst: list[UnmarshalerFactory] = list(
            u_cfg.lst if u_cfg is not None else DEFAULT_STANDARD_FACTORIES.unmarshaler_factories,
        )

        m_new = False
        u_new = False

        for f in factories:
            k = False

            if isinstance(f, MarshalerFactory):
                m_lst[0:0] = [f]
                m_new = True
                k = True

            if isinstance(f, UnmarshalerFactory):
                u_lst[0:0] = [f]
                u_new = True
                k = True

            if not k:
                raise TypeError(f)

        if m_new:
            cfgs.update(None, StandardMarshalerFactories(m_lst), mode='override')
        if u_new:
            cfgs.update(None, StandardUnmarshalerFactories(u_lst), mode='override')
