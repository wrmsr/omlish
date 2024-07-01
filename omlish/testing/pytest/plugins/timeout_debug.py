from ... import pydevd
from ._registry import register


@register
class TimeoutDebugPlugin:

    def pytest_collection(self, session):
        config = session.config
        setup = pydevd.get_setup()
        if setup is not None:
            if hasattr(config, '_env_timeout'):
                session.config._env_timeout = None
