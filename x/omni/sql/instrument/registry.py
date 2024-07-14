import functools
import threading
import typing as ta

import pkg_resources
import sqlalchemy as sa
import sqlalchemy.dialects  # noqa

from ... import check
from ... import lang
from .dialect import InstrumentationDialectMixin


AFFIX = 'o'

_CLS_NAME_SUFFIX = '__' + __name__.replace('.', '_')


@lang.context_wrapped(threading.RLock())
def create_instrumented_dialect(base: ta.Type[sa.engine.Dialect]) -> ta.Type[sa.engine.Dialect]:
    check.issubclass(base, sa.engine.Dialect)
    name = base.__name__ + _CLS_NAME_SUFFIX

    if name in globals():
        existing = globals()[name]
        check.issubclass(existing, sa.engine.Dialect)
        check.issubclass(existing, InstrumentationDialectMixin)
        if not issubclass(existing, base):
            raise NameError(name)
        return existing

    check.not_empty(base.driver)  # type: ignore  # noqa
    dialect = type(name, (InstrumentationDialectMixin, base), {'__module__': __name__})
    globals()[name] = dialect
    rname = f'{AFFIX}_{base.name}.{base.driver}'  # type: ignore  # noqa
    sa.dialects.registry.register(rname, dialect.__module__, name)
    return dialect  # noqa


class _Dist(pkg_resources.Distribution):

    class _EntryPoint(pkg_resources.EntryPoint):
        def __init__(self):
            super().__init__(_Dist._EntryPoint._Name(), __name__)

        def load(self, *args, **kwargs):
            n = check.not_none(self.name._name)
            check.state(n.startswith(AFFIX + '_'))
            on = n[len(AFFIX) + 1:]
            cls = sa.dialects.registry.load(on)
            return create_instrumented_dialect(cls)

        @functools.total_ordering
        class _Name:
            _DEFAULT = '_dummy'

            def __init__(self):
                super().__init__()
                self._name = None

            def __hash__(self):
                if self._name is None:
                    self._name = self._DEFAULT
                return hash(self._name)

            def __eq__(self, other):
                if not isinstance(other, str):
                    raise TypeError
                if self._name is not None:
                    return other == self._name
                if not other.startswith(AFFIX + '_'):
                    self._name = self._DEFAULT
                    return False
                self._name = other
                return True

            def __lt__(self, other):
                if self._name is None:
                    self._name = self._DEFAULT
                return self._name < other

    def get_entry_map(self, group=None):
        if group == 'sqlalchemy.dialects':
            return {__name__: _Dist._EntryPoint()}
        return {}

    def activate(self, *args, **kwargs):
        pass


pkg_resources.working_set.add(_Dist(), __name__.replace('.', '_'))
