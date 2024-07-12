import typing as ta

from ... import check
from ...testing.pytest import inject as pti
from ...tests.docker import ComposeServices
from ..dbs import DbSpec
from ..dbs import DbTypes
from ..dbs import UrlDbLoc


def _get_compose_port(cfg: ta.Mapping[str, ta.Any], default: int) -> int:
    return check.single(
        int(l)
        for p in cfg['ports']
        for l, r in [p.split(':')]
        if int(r) == default
    )


@pti.bind('function')
class Dbs:
    def __init__(self, compose_services: ComposeServices) -> None:
        super().__init__()
        self._compose_services = compose_services

    def specs(self) -> ta.Mapping[str, DbSpec]:
        svcs = self._compose_services.compose_config().get_services()
        lst: list[DbSpec] = []

        if (mysql := svcs.get('mysql')):
            port = _get_compose_port(mysql, check.not_none(DbTypes.MYSQL.default_port))
            env = mysql['environment']
            lst.append(DbSpec(
                'mysql',
                DbTypes.MYSQL,
                UrlDbLoc(f'mysql://root:{env["MYSQL_ROOT_PASSWORD"]}@localhost:{port}')
            ))

        if (postgres := svcs.get('postgres')):
            port = _get_compose_port(postgres, check.not_none(DbTypes.POSTGRES.default_port))
            env = postgres['environment']
            lst.append(DbSpec(
                'postgres',
                DbTypes.MYSQL,
                UrlDbLoc(f'postgres://{env["POSTGRES_USER"]}:{env["POSTGRES_PASSWORD"]}@localhost:{port}')
            ))

        return {s.name: s for s in lst}
