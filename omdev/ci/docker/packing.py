# ruff: noqa: UP006 UP007 UP045
import asyncio
import os.path
import shlex
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.cached import async_cached_nullary
from omlish.lite.cached import cached_nullary
from omlish.lite.contextmanagers import ExitStacked
from omlish.logs.utils import log_timing_context
from omlish.os.temp import temp_dir_context

from ...oci.building import BuiltOciImageIndexRepository
from ...oci.pack.repositories import OciPackedRepositoryBuilder
from ...oci.repositories import DirectoryOciRepository


##


class PackedDockerImageIndexRepositoryBuilder(ExitStacked):
    def __init__(
            self,
            *,
            image_id: str,

            temp_dir: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._image_id = image_id

        self._given_temp_dir = temp_dir

    @cached_nullary
    def _temp_dir(self) -> str:
        if (given := self._given_temp_dir) is not None:
            return given
        else:
            return self._enter_context(temp_dir_context())  # noqa

    #

    @async_cached_nullary
    async def _save_to_dir(self) -> str:
        save_dir = os.path.join(self._temp_dir(), 'built-image')
        os.mkdir(save_dir)

        with log_timing_context(f'Saving docker image {self._image_id}'):
            await asyncio_subprocesses.check_call(
                ' | '.join([
                    f'docker save {shlex.quote(self._image_id)}',
                    f'tar x -C {shlex.quote(save_dir)}',
                ]),
                shell=True,
            )

        return save_dir

    #

    @async_cached_nullary
    async def build(self) -> BuiltOciImageIndexRepository:
        saved_dir = await self._save_to_dir()

        with OciPackedRepositoryBuilder(
                DirectoryOciRepository(saved_dir),

                temp_dir=self._temp_dir(),
        ) as prb:
            return await asyncio.get_running_loop().run_in_executor(None, prb.build)
