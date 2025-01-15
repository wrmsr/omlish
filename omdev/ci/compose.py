# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - fix rmi - only when not referenced anymore
"""
import contextlib
import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.contextmanagers import ExitStacked
from omlish.lite.contextmanagers import defer
from omlish.lite.json import json_dumps_pretty
from omlish.subprocesses import subprocesses

from .utils import make_temp_file
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


class DockerComposeRun(ExitStacked):
    @dc.dataclass(frozen=True)
    class Config:
        compose_file: str
        service: str

        image: str

        run_cmd: ta.Sequence[str]

        #

        run_options: ta.Optional[ta.Sequence[str]] = None

        cwd: ta.Optional[str] = None

        #

        no_dependency_cleanup: bool = False

        #

        def __post_init__(self) -> None:
            check.not_isinstance(self.run_cmd, str)

            check.not_isinstance(self.run_options, str)

    def __init__(self, cfg: Config) -> None:
        super().__init__()

        self._cfg = cfg

        self._subprocess_kwargs = {
            **(dict(cwd=self._cfg.cwd) if self._cfg.cwd is not None else {}),
        }

    #

    @property
    def image_tag(self) -> str:
        pfx = 'sha256:'
        if (image := self._cfg.image).startswith(pfx):
            image = image[len(pfx):]

        return f'{self._cfg.service}:{image}'

    @cached_nullary
    def tag_image(self) -> str:
        image_tag = self.image_tag

        subprocesses.check_call(
            'docker',
            'tag',
            self._cfg.image,
            image_tag,
            **self._subprocess_kwargs,
        )

        def delete_tag() -> None:
            subprocesses.check_call(
                'docker',
                'rmi',
                image_tag,
                **self._subprocess_kwargs,
            )

        self._enter_context(defer(delete_tag))  # noqa

        return image_tag

    #

    def _rewrite_compose_dct(self, in_dct: ta.Dict[str, ta.Any]) -> ta.Dict[str, ta.Any]:
        out = dict(in_dct)

        #

        in_services = in_dct['services']
        out['services'] = out_services = {}

        #

        in_service: dict = in_services[self._cfg.service]
        out_services[self._cfg.service] = out_service = dict(in_service)

        out_service['image'] = self.image_tag

        for k in ['build', 'platform']:
            if k in out_service:
                del out_service[k]

        out_service['links'] = [
            f'{l}:{l}' if ':' not in l else l
            for l in out_service.get('links', [])
        ]

        #

        depends_on = in_service.get('depends_on', [])

        for dep_service, in_dep_service_dct in list(in_services.items()):
            if dep_service not in depends_on:
                continue

            out_dep_service: dict = dict(in_dep_service_dct)
            out_services[dep_service] = out_dep_service

            out_dep_service['ports'] = []

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

    def _cleanup_dependencies(self) -> None:
        subprocesses.check_call(
            'docker',
            'compose',
            '-f', self.rewrite_compose_file(),
            'down',
        )

    def run(self) -> None:
        self.tag_image()

        compose_file = self.rewrite_compose_file()

        with contextlib.ExitStack() as es:
            if not self._cfg.no_dependency_cleanup:
                es.enter_context(defer(self._cleanup_dependencies))  # noqa

            subprocesses.check_call(
                'docker',
                'compose',
                '-f', compose_file,
                'run',
                '--rm',
                *self._cfg.run_options or [],
                self._cfg.service,
                *self._cfg.run_cmd,
                **self._subprocess_kwargs,
            )
