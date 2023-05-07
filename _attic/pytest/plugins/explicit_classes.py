import _pytest.mark.structures

from ._registry import register_plugin


@register_plugin
class ExplicitClassesPlugin:

    def pytest_configure(self, config):
        config.addinivalue_line('markers', 'test_class: mark class as test class')

    def pytest_pycollect_makeitem(self, collector, name, obj):
        if isinstance(obj, type):
            if not any(m.name == 'test_class' for m in _pytest.mark.structures.get_unpacked_marks(obj)):
                return []
        return None
