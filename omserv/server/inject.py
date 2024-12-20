from omlish import inject as inj

from .config import Config


def bind_server(
        config: Config,
) -> inj.Elemental:
    return inj.as_elements(
        inj.bind(config),
    )
