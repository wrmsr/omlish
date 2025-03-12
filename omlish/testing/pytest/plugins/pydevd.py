from ....diag import pydevd as opd
from ._registry import register


@register
class PydevdPlugin:
    def pytest_addoption(self, parser):
        parser.addoption('--no-pydevd', action='store_true', default=False, help='Disables pydevd debugging')

    def pytest_collection(self, session):
        if opd.get_setup() is not None:
            if hasattr(session.config, '_env_timeout'):
                session.config._env_timeout = None  # noqa

            # if (dbg := opd.get_global_debugger()) is not None:
            #     dbg.set_unit_tests_debugging_mode()

    # def pytest_exception_interact(self, node, call, report):
    #     if opd.get_setup() is not None:
    #         if not node.session.config.option.no_pydevd:
    #             opd.debug_unhandled_exception(call.excinfo._excinfo)  # noqa
    #
    #     return report
