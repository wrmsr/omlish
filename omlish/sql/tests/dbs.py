import typing as ta

from ... import check
from ...docker import get_compose_port
from ...docker import is_likely_in_docker
from ...docker.tests.services import ComposeServices
from ...testing.pytest import inject as pti
from ..dbs import DbSpec
from ..dbs import DbTypes
from ..dbs import UrlDbLoc


@pti.bind('function')
class Dbs:
    def __init__(self, compose_services: ComposeServices) -> None:
        super().__init__()
        self._compose_services = compose_services

    def specs(self) -> ta.Mapping[str, DbSpec]:
        svcs = self._compose_services.config().get_services()
        lst: list[DbSpec] = []

        in_docker = is_likely_in_docker()

        if (mysql := svcs.get('mysql')):
            if in_docker:
                host = self._compose_services.prefix + 'mysql'
                port = DbTypes.MYSQL.default_port
            else:
                host = '127.0.0.1'
                port = get_compose_port(mysql, check.not_none(DbTypes.MYSQL.default_port))

            env = mysql['environment']
            lst.append(DbSpec(
                'mysql',
                DbTypes.MYSQL,
                UrlDbLoc(f'mysql://root:{env["MYSQL_ROOT_PASSWORD"]}@{host}:{port}'),
            ))

        if (postgres := svcs.get('postgres')):
            if in_docker:
                host = self._compose_services.prefix + 'postgres'
                port = DbTypes.POSTGRES.default_port
            else:
                host = '127.0.0.1'
                port = get_compose_port(postgres, check.not_none(DbTypes.POSTGRES.default_port))

            env = postgres['environment']
            lst.append(DbSpec(
                'postgres',
                DbTypes.POSTGRES,
                UrlDbLoc(f'postgresql://{env["POSTGRES_USER"]}:{env["POSTGRES_PASSWORD"]}@{host}:{port}'),
            ))

        return {s.name: s for s in lst}
