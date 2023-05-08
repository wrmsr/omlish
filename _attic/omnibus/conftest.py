import os.path

# FIXME: omnibus-all
# with open(os.path.join(os.path.dirname(__file__), '../setup.py'), 'r') as f:
#     _setup_header = f.readline()
# if _setup_header.strip() != '#@omnibus':
#     raise EnvironmentError('Should not be present')


_BASE_DIR = os.path.abspath(os.path.dirname(__file__))
_EXT_DIR = os.path.join(_BASE_DIR, '_ext')


from omnibus.lang.imports import ignore_unstable_warn  # noqa

ignore_unstable_warn()


from .dev.pytest.plugins import ci  # noqa

if 'OMNIBUS_CI' in os.environ:
    ci.set_ci(int(os.environ.get('OMNIBUS_CI', '0').strip()) != 0)


from .docker.dev import pytest as dckp  # noqa
from .inject.dev import pytest as injp  # noqa

injp.bind_instance(injp.Session, dckp.Prefix('omnibus-'))
injp.bind_instance(injp.Session, dckp.ComposePath(os.path.join(os.path.dirname(__file__), '../docker/docker-compose.yml')))  # noqa


from .dev.pytest import plugins  # noqa


def pytest_addhooks(pluginmanager):
    for plugin in plugins.ALL:
        pluginmanager.register(plugin())


def pytest_configure(config):
    config.addinivalue_line('filterwarnings', 'ignore:omnibus module is marked as unstable::omnibus.*:')


def pytest_ignore_collect(path, config):
    path_dir = os.path.abspath(os.path.dirname(path))
    if plugins.switches.is_disabled(config, 'ext') and path_dir.startswith(_EXT_DIR):
        return True
