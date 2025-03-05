# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - docstring
 - timebomb
 - auto-discover available ports
"""
import dataclasses as dc
import os
import typing as ta


##


@dc.dataclass(frozen=True)
class DockerPortRelay:
    """
    Uses roughly the following command to forward connections from inside docker-for-mac's vm to the mac host:

      docker run --rm -i -p 5001:5000 alpine/socat -d -d TCP-LISTEN:5000,fork,reuseaddr TCP:host.docker.internal:5021

    This allows requests made by the docker daemon running inside the vm to `host.docker.internal:5001` to be forwarded
    to the mac host on port 5021. The reason for this is to be able to use a docker registry running locally directly on
    the host mac - specifically to be able to do so with ssl certificate checking disabled (which docker will only do on
    localhost, which on a mac in the vm isn't actually the mac host - hence the necessity of the relay).
    """

    docker_port: int  # port
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
            name = f'docker_port_relay-{os.getpid()}-{self.docker_port}-{self.intermediate_port}-{self.host_port}'

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
