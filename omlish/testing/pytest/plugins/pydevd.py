from ... import pydevd as opd
from ._registry import register


@register
class PydevdPlugin:

    def pytest_collection(self, session):
        setup = opd.get_setup()
        if setup is not None:
            if hasattr(session.config, '_env_timeout'):
                session.config._env_timeout = None  # noqa
