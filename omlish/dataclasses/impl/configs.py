import dataclasses as dc


##


PACKAGE_CONFIG_FILE_NAME = '.dataclasses.json'


@dc.dataclass(frozen=True, kw_only=True)
class PackageConfig:
    codegen: bool = False
