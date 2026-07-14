# ruff: noqa: UP006 UP007 UP043 UP045
import abc
import contextlib
import shlex
import typing as ta

from omcore.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omcore.lite.abstract import Abstract
from omcore.lite.timing import log_timing_context
from omcore.os.temp import temp_dir_context

from ...specs.oci.repositories import DirectoryOciRepository
from ...specs.oci.repositories import OciRepository


##


class DockerImageRepositoryOpener(Abstract):
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
