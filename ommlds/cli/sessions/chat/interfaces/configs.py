"""
TODO:
 - obviously, subclasses of InterfaceConfig
  - this is really just another instance of the whole `argparse -> config -> inject` flow
"""
import typing as ta

from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True, kw_only=True)
class InterfaceConfig:
    interactive: bool = False

    use_textual: bool = False

    use_readline: bool | ta.Literal['auto'] = 'auto'

    enable_tools: bool = False
    dangerous_no_tool_confirmation: bool = False
