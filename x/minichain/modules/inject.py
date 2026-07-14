from omlish import check
from omlish import inject as inj

from ..registries.globals import get_global_registry
from .configs import ModuleConfig
from .descriptors import ModuleDescriptor


##


def bind_module(cfg: ModuleConfig) -> inj.Elements:
    rt = get_global_registry().get_type(ModuleDescriptor)

    mds = [
        md
        for rte in rt.entries.values()
        if isinstance(cfg, (md := check.isinstance(rte.resolve(), ModuleDescriptor)).config_cls)
    ]
    if not mds:
        raise TypeError(cfg)

    return inj.as_elements(*[
        md.binder(cfg)
        for md in mds
    ])
