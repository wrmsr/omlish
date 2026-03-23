from omlish import inject as inj
from omlish import lang

from ...backends.configs import BackendConfig
from ...backends.types import DefaultBackendName
from ..base import Mode
from .configs import DEFAULT_BACKEND
from .configs import CompletionConfig


with lang.auto_proxy_import(globals()):
    from ...backends import inject as _backends
    from . import mode as _mode


##


def bind_completion(cfg: CompletionConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind(cfg),
        inj.bind(Mode, to_ctor=_mode.CompletionMode, singleton=True),
    ])

    #

    els.extend([
        _backends.bind_backends(BackendConfig(
            backend=cfg.backend,
        )),

        inj.bind(DefaultBackendName, to_const=DEFAULT_BACKEND),
    ])

    #

    return inj.as_elements(*els)
