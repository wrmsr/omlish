# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import os
import typing as ta


@dc.dataclass(frozen=True)
class DockerPortRelay:
    docker_port: int
    host_port: int

    name: ta.Optional[str] = None

    DEFAULT_HOST_NAME: ta.ClassVar[str] = 'host.docker.internal'
    host_name: str = DEFAULT_HOST_NAME

    DEFAULT_INTERMEDIATE_PORT: ta.ClassVar[int] = 5000
    intermediate_port: int = DEFAULT_INTERMEDIATE_PORT

    DEFAULT_IMAGE: ta.ClassVar[str] = 'alpine/socat'
    image: str = DEFAULT_IMAGE

    def socat_args(self) -> ta.List[str]:
        return [
            '-d',
            f'TCP-LISTEN:{self.intermediate_port},fork,reuseaddr',
            f'TCP:{self.host_name}:{self.host_port}',
        ]

    def run_args(self) -> ta.List[str]:
        if (name := self.name) is None:
            name = f'docker_port_relay-{os.getpid()}'

        return [
            '--name', name,
            '--rm',
            '-p', f'{self.docker_port}:{self.intermediate_port}',
            self.image,
            *self.socat_args(),
        ]

    def run_cmd(self) -> ta.List[str]:
        return [
            'docker',
            'run',
            '-i',
            *self.run_args(),
        ]
