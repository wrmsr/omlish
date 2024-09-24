import dataclasses as dc


@dc.dataclass(frozen=True)
class CliModule:
    cmd_name: str
    mod_name: str
