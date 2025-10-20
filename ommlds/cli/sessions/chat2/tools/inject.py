from omlish import inject as inj
from omlish import lang


with lang.auto_proxy_import(globals()):
    from . import confirmation as _confirmation  # noqa
    from . import execution as _execution


##


def bind_tools() -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(inj.bind(_execution.ToolUseExecutor, to_ctor=_execution.ToolUseExecutorImpl, singleton=True))

    #

    return inj.as_elements(*els)
