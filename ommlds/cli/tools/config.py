from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True, kw_only=True)
class ToolsConfig:
    enable_fs_tools: bool = False

    enable_unsafe_bash_tool: bool = False

    enable_test_weather_tool: bool = False
