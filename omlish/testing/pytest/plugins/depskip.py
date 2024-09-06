"""
https://github.com/pytest-dev/pytest-asyncio/blob/b1dc0c3e2e82750bdc6dbdf668d519aaa89c036c/pytest_asyncio/plugin.py#L657
"""
from ....diag import pydevd as opd
from ._registry import register


@register
class PydevdPlugin:

    def pytest_collection(self, session):
        setup = opd.get_setup()
        if setup is not None:
            if hasattr(session.config, '_env_timeout'):
                session.config._env_timeout = None  # noqa
