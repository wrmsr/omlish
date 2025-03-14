# ruff: noqa: UP006 UP007
"""
TODO:
 - fix rmi - only when not referenced anymore
"""
import contextlib
import dataclasses as dc
import itertools
import os.path
import shlex
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.contextmanagers import AsyncExitStacked
from omlish.lite.contextmanagers import adefer
from omlish.lite.contextmanagers import defer
from omlish.lite.json import json_dumps_pretty
from omlish.os.temp import make_temp_file

from .shell import ShellCmd
from .utils import read_yaml_file


##


def get_compose_service_dependencies(
        compose_file: str,
        service: str,
) -> ta.Dict[str, str]:
    compose_dct = read_yaml_file(compose_file)

    services = compose_dct['services']
    service_dct = services[service]

    out = {}
    for dep_service in service_dct.get('depends_on', []):
        dep_service_dct = services[dep_service]
        out[dep_service] = dep_service_dct['image']

    return out


##


class DockerComposeRun(AsyncExitStacked):
    @dc.dataclass(frozen=True)
    class Config:
        compose_file: str
        service: str

        image: str

        cmd: ShellCmd

        #

        run_options: ta.Optional[ta.Sequence[str]] = None

        cwd: ta.Optional[str] = None

        #

        no_dependencies: bool = False
        no_dependency_cleanup: bool = False

        #

        def __post_init__(self) -> None:
            check.not_isinstance(self.run_options, str)

    def __init__(self, cfg: Config) -> None:
        super().__init__()

        self._cfg = cfg

        self._subprocess_kwargs = {
            **(dict(cwd=self._cfg.cwd) if self._cfg.cwd is not None else {}),
        }

    #

    def _rewrite_compose_dct(self, in_dct: ta.Dict[str, ta.Any]) -> ta.Dict[str, ta.Any]:
        out = dict(in_dct)

        #

        in_services = in_dct['services']
        out['services'] = out_services = {}

        #

        in_service: dict = in_services[self._cfg.service]
        out_services[self._cfg.service] = out_service = dict(in_service)

        out_service['image'] = self._cfg.image

        for k in ['build', 'platform']:
            out_service.pop(k, None)

        #

        if not self._cfg.no_dependencies:
            depends_on = in_service.get('depends_on', [])

            for dep_service, in_dep_service_dct in list(in_services.items()):
                if dep_service not in depends_on:
                    continue

                out_dep_service: dict = dict(in_dep_service_dct)
                out_services[dep_service] = out_dep_service

                out_dep_service['ports'] = []

        else:
            out_service['depends_on'] = []

        #

        return out

    @cached_nullary
    def rewrite_compose_file(self) -> str:
        in_dct = read_yaml_file(self._cfg.compose_file)

        out_dct = self._rewrite_compose_dct(in_dct)

        #

        out_compose_file = make_temp_file()
        self._enter_context(defer(lambda: os.unlink(out_compose_file)))  # noqa

        compose_json = json_dumps_pretty(out_dct)

        with open(out_compose_file, 'w') as f:
            f.write(compose_json)

        return out_compose_file

    #

    async def _cleanup_dependencies(self) -> None:
        await asyncio_subprocesses.check_call(
            'docker',
            'compose',
            '-f', self.rewrite_compose_file(),
            'down',
        )

    async def run(self) -> None:
        compose_file = self.rewrite_compose_file()

        async with contextlib.AsyncExitStack() as es:
            if not (self._cfg.no_dependencies or self._cfg.no_dependency_cleanup):
                await es.enter_async_context(adefer(self._cleanup_dependencies))  # noqa

            sh_cmd = ' '.join([
                'docker',
                'compose',
                '-f', compose_file,
                'run',
                '--rm',
                *itertools.chain.from_iterable(
                    ['-e', k]
                    for k in (self._cfg.cmd.env or [])
                ),
                *(self._cfg.run_options or []),
                self._cfg.service,
                'sh', '-c', shlex.quote(self._cfg.cmd.s),
            ])

            run_cmd = dc.replace(self._cfg.cmd, s=sh_cmd)

            await run_cmd.run(
                asyncio_subprocesses.check_call,
                **self._subprocess_kwargs,
            )
