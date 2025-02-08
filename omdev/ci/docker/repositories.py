# ruff: noqa: UP006 UP007
import abc
import contextlib
import shlex
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.timing import log_timing_context
from omlish.os.temp import temp_dir_context

from ...oci.repositories import DirectoryOciRepository
from ...oci.repositories import OciRepository


##


class DockerImageRepositoryOpener(abc.ABC):
    @abc.abstractmethod
    def open_docker_image_repository(self, image: str) -> ta.AsyncContextManager[OciRepository]:
        raise NotImplementedError


#


class DockerImageRepositoryOpenerImpl(DockerImageRepositoryOpener):
    @contextlib.asynccontextmanager
    async def open_docker_image_repository(self, image: str) -> ta.AsyncGenerator[OciRepository, None]:
        with temp_dir_context() as save_dir:
            with log_timing_context(f'Saving docker image {image}'):
                await asyncio_subprocesses.check_call(
                    ' | '.join([
                        f'docker save {shlex.quote(image)}',
                        f'tar x -C {shlex.quote(save_dir)}',
                    ]),
                    shell=True,
                )

            yield DirectoryOciRepository(save_dir)
