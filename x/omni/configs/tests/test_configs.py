from .. import configs as configs_
from ... import dataclasses as dc


class DbConfig(configs_.Config):
    url: str
    comment: str = dc.field(doc='comment')


class ExtraConfig(configs_.Config):
    extra0: int = 5
    extra1 = 6
    extra2: int


class ExtraDbConfig(DbConfig, ExtraConfig):
    pass


class BytesUrlConfig(configs_.Config):
    url: bytes


class BytesUrlDbConfig(BytesUrlConfig, DbConfig):
    pass


class MetadataConfig(configs_.Config):
    thing: str = dc.field()


def test_configs():
    db_config = DbConfig(
        url='a url',
        comment='a comment',
    )
    assert db_config.url == 'a url'


class EnumCfg(dc.Enum, configs_.Config):
    pass


class AEnumCfg(EnumCfg):
    pass


class BEnumCfg(EnumCfg):
    pass
