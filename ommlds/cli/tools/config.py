from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True, kw_only=True)
class ToolsConfig:
    enable_fs_tools: bool = False
    enable_todo_tools: bool = False

    enable_unsafe_tools_do_not_use_lol: bool = False

    enable_test_weather_tool: bool = False
