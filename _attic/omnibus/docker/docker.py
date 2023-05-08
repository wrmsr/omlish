"""
TODO:
 - Dockerfile r/w


github actions:
  ['12', 'devices', '/actions_job/44115d67f9b6631e4ba9be08855286723979dfb855525c7dd9c88190f1343cff']

ARM DOCKER
 - https://www.stereolabs.com/docs/docker/building-arm-container-on-x86/
 - https://github.com/multiarch/qemu-user-static/
 - https://hub.docker.com/r/arm64v8/ubuntu/
 - https://docs.docker.com/docker-for-mac/multi-arch/
 - https://github.com/docker/buildx#installing
"""
import contextlib
import io
import re
import sys
import tarfile
import time
import typing as ta

import pkg_resources

if ta.TYPE_CHECKING:
    import docker.client

from .. import check
from .. import lang


LINUX_PLATFORMS = ('linux', 'linux2')


@lang.cached_nullary
def is_in_docker() -> bool:
    if sys.platform not in LINUX_PLATFORMS:
        return False
    try:
        with open('/proc/1/cgroup', 'r') as f:
            buf = f.read()
    except OSError:
        return False
    tups = [line.strip().split(':') for line in buf.strip().splitlines()]
    dct = {k: tup for tup in tups for k in tup[1].split(',')}
    return all(k in dct and dct[k][2].startswith('/docker/') for k in {'cpu', 'memory'})


def get_client(**kwargs) -> 'docker.client.DockerClient':
    import docker

    kwargs.setdefault('timeout', 1)
    kwargs.setdefault('version', 'auto')

    client = docker.from_env(**kwargs)
    client.version()
    return client


def close_client(client):
    try:
        for adapter in client.api.adapters.values():
            try:
                adapter.close()
            except AttributeError:
                pass
    except AttributeError:
        pass


@contextlib.contextmanager
def client_context(**kwargs) -> ta.Iterator['docker.client.DockerClient']:
    client = get_client(**kwargs)
    try:
        yield client
    finally:
        close_client(client)


DOCKER_COMPOSE_PATTERN = re.compile(r'^((docker|compose)_)?(?P<name>.+?)(_[0-9]+(_[0-9a-fA-f]+)?)?$')


def find_container_by_name(containers: ta.Iterable[ta.Dict], name: str) -> ta.Iterator[ta.Dict]:
    for c in containers:
        cname = c.name  # type: ignore
        if cname == name:
            yield c
        else:
            m = DOCKER_COMPOSE_PATTERN.match(cname)
            if m is not None and m.groupdict()['name'] == name:
                yield c


def get_container_tcp_host_port(container, port) -> ta.Optional[ta.Tuple[str, int]]:
    try:
        entry = container.attrs['NetworkSettings']['Ports'][f'{port}/tcp'][0]
    except (KeyError, IndexError):
        return None
    return entry['HostIp'], int(entry['HostPort'])


def get_container_tcp_endpoints(
        client,
        name_port_pairs: ta.Iterable[ta.Tuple[str, int]]
) -> ta.Dict[ta.Tuple[str, int], ta.Tuple[str, int]]:
    ret = {}
    containers = client.containers.list()
    for name, internal_port in name_port_pairs:
        found_containers = list(find_container_by_name(containers, name))
        if len(found_containers) != 1:
            raise EnvironmentError(f'Failed to find container: {name!r}')
        [container] = found_containers
        hostname, external_port = check.not_none(get_container_tcp_host_port(container, internal_port))
        ret[(name, internal_port)] = (hostname, external_port)

    return ret


class TarBuilder:

    def __init__(self, fileobj=None) -> None:
        if fileobj is None:
            fileobj = io.BytesIO()
        self._fileobj = fileobj
        self._tar: ta.Optional[tarfile.TarFile] = None

    def flip(self):
        self._fileobj.seek(0)
        return self._fileobj

    def __enter__(self) -> 'TarBuilder':
        self._tar = tarfile.TarFile(fileobj=self._fileobj, mode='w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._tar is not None:
            self._tar.close()

    def add_data(self, name: str, data: bytes) -> None:
        tar_info = tarfile.TarInfo(name=name)
        tar_info.size = len(data)
        tar_info.mtime = int(time.time())
        # tarinfo.mode = 0600
        self._tar.addfile(tar_info, io.BytesIO(data))

    def add_file(self, name: str, file_path) -> None:
        with open(file_path, 'rb') as f:
            data = f.read()
        self.add_data(name, data)

    def add_resource(self, name: str, package: str, resource: str) -> None:
        data = pkg_resources.resource_stream(package, resource).read()
        self.add_data(name, data)
