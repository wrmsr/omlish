from omlish import check
from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc
from .injection import tool_catalog_entries


with lang.auto_proxy_import(globals()):
    from . import confirmation as _confirmation  # noqa
    from . import execution as _execution


##


def bind_tools(
        *,
        interactive: bool = False,
        dangerous_no_confirmation: bool = False,
) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(inj.bind(mc.ToolCatalog, singleton=True))

    #

    els.append(tool_catalog_entries().bind_items_provider(singleton=True))

    from ....tools.weather import WEATHER_TOOL
    els.append(tool_catalog_entries().bind_item_consts(WEATHER_TOOL))

    #

    els.append(inj.bind(_execution.ToolUseExecutor, to_ctor=_execution.ToolUseExecutorImpl, singleton=True))

    #

    if not dangerous_no_confirmation:
        check.state(interactive, 'Interactive is required for tool confirmation')
        els.append(inj.bind(_confirmation.ToolExecutionConfirmation, to_ctor=_confirmation.InteractiveToolExecutionConfirmation, singleton=True))  # noqa

    #

    return inj.as_elements(*els)
