"""
TODO:
 - more logging options
 - a more powerful interface would be run_fn_with_bootstrap..
 - ./python -m gprof2dot -f pstats prof.pstats | dot -Tpdf -o prof.pstats.pdf && open prof.pstats.pdf
 - multiprocess profiling - afterfork, suffix with pid

TODO diag:
 - tracemalloc
 - yappi
 - stackscope
 - https://github.com/pythonspeed/filprofiler
 - https://pypi.org/project/guppy3/
 - https://pypi.org/project/memory-profiler/
 - https://pypi.org/project/Pympler/


TODO new items:
 - packaging fixups
 - daemonize ( https://github.com/thesharp/daemonize/blob/master/daemonize.py )
"""
# ruff: noqa: UP006
import contextlib
import typing as ta

from .. import lang
from . import diag  # noqa
from . import sys  # noqa
from .base import Bootstrap
from .base import ContextBootstrap
from .base import SimpleBootstrap


##


BOOTSTRAP_TYPES_BY_NAME: ta.Mapping[str, ta.Type[Bootstrap]] = {  # noqa
    lang.snake_case(*lang.split_string_casing(cls.__name__[:-len('Bootstrap')])): cls
    for cls in lang.deep_subclasses(Bootstrap, concrete_only=True)
}

BOOTSTRAP_TYPES_BY_CONFIG_TYPE: ta.Mapping[ta.Type[Bootstrap.Config], ta.Type[Bootstrap]] = {
    cls.Config: cls
    for cls in BOOTSTRAP_TYPES_BY_NAME.values()
}


##


class BootstrapHarness:
    def __init__(self, lst: ta.Sequence[Bootstrap]) -> None:
        super().__init__()

        self._lst = lst

    @contextlib.contextmanager
    def __call__(self) -> ta.Iterator[None]:
        with contextlib.ExitStack() as es:
            for c in self._lst:
                if isinstance(c, SimpleBootstrap):
                    c.run()
                elif isinstance(c, ContextBootstrap):
                    es.enter_context(c.enter())
                else:
                    raise TypeError(c)

            yield


##


@contextlib.contextmanager
def bootstrap(*cfgs: Bootstrap.Config) -> ta.Iterator[None]:
    with BootstrapHarness([
        BOOTSTRAP_TYPES_BY_CONFIG_TYPE[type(c)](c)
        for c in cfgs
    ])():
        yield
