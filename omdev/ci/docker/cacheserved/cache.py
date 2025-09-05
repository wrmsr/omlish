# ruff: noqa: UP006 UP007 UP045
import asyncio
import contextlib
import dataclasses as dc
import json
import os.path
import typing as ta

from omlish.asyncs.asyncio.sockets import asyncio_wait_until_can_connect
from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.check import check
from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj
from omlish.lite.timeouts import Timeout
from omlish.lite.timeouts import TimeoutLike
from omlish.logs.modules import get_module_logger

from ....dataserver.server import DataServer
from ....dataserver.targets import DataServerTarget
from ....oci.building import build_oci_index_repository
from ....oci.data import get_single_leaf_oci_image_index
from ....oci.dataserver import build_oci_repository_data_server_routes
from ....oci.loading import read_oci_repository_root_index
from ....oci.pack.repositories import OciPackedRepositoryBuilder
from ....oci.repositories import OciRepository
from ...cache import DataCache
from ...cache import read_data_cache_data
from ..cache import DockerCache
from ..cache import DockerCacheKey
from ..dataserver import DockerDataServer
from ..repositories import DockerImageRepositoryOpener
from .manifests import CacheServedDockerImageManifest
from .manifests import build_cache_served_docker_image_data_server_routes
from .manifests import build_cache_served_docker_image_manifest


log = get_module_logger(globals())  # noqa


##


class CacheServedDockerCache(DockerCache):
    @dc.dataclass(frozen=True)
    class Config:
        port: int = 5021

        repack: bool = True

        key_prefix: ta.Optional[str] = 'cs'

        #

        pull_run_cmd: ta.Optional[str] = 'true'

        #

        server_start_timeout: TimeoutLike = 5.
        server_start_sleep: float = .1

    def __init__(
            self,
            *,
            config: Config = Config(),

            image_repo_opener: DockerImageRepositoryOpener,
            data_cache: DataCache,
    ) -> None:
        super().__init__()

        self._config = config

        self._image_repo_opener = image_repo_opener
        self._data_cache = data_cache

    async def load_cache_docker_image(self, key: DockerCacheKey) -> ta.Optional[str]:
        if (kp := self._config.key_prefix) is not None:
            key = key.append_prefix(kp)

        if (manifest_data := await self._data_cache.get_data(str(key))) is None:
            return None

        manifest_bytes = await read_data_cache_data(manifest_data)

        manifest: CacheServedDockerImageManifest = unmarshal_obj(
            json.loads(manifest_bytes.decode('utf-8')),
            CacheServedDockerImageManifest,
        )

        async def make_cache_key_target(target_cache_key: str, **target_kwargs: ta.Any) -> DataServerTarget:  # noqa
            cache_data = check.not_none(await self._data_cache.get_data(target_cache_key))

            if isinstance(cache_data, DataCache.BytesData):
                return DataServerTarget.of(
                    cache_data.data,
                    **target_kwargs,
                )

            elif isinstance(cache_data, DataCache.FileData):
                return DataServerTarget.of(
                    file_path=cache_data.file_path,
                    **target_kwargs,
                )

            elif isinstance(cache_data, DataCache.UrlData):
                return DataServerTarget.of(
                    url=cache_data.url,
                    methods=['GET'],
                    **target_kwargs,
                )

            else:
                raise TypeError(cache_data)

        data_server_routes = await build_cache_served_docker_image_data_server_routes(
            manifest,
            make_cache_key_target,
        )

        data_server = DataServer(DataServer.HandlerRoute.of_(*data_server_routes))

        image_url = f'localhost:{self._config.port}/{key!s}'

        async with DockerDataServer(
                self._config.port,
                data_server,
                handler_log=log,
        ) as dds:
            dds_run_task = asyncio.create_task(dds.run())
            try:
                timeout = Timeout.of(self._config.server_start_timeout)

                await asyncio_wait_until_can_connect(
                    'localhost',
                    self._config.port,
                    timeout=timeout,
                    on_fail=lambda _: log.exception('Failed to connect to cache server - will try again'),
                    sleep_s=self._config.server_start_sleep,
                )

                if (prc := self._config.pull_run_cmd) is not None:
                    pull_cmd = [
                        'run',
                        '--rm',
                        image_url,
                        prc,
                    ]
                else:
                    pull_cmd = [
                        'pull',
                        image_url,
                    ]

                await asyncio_subprocesses.check_call(
                    'docker',
                    *pull_cmd,
                )

            finally:
                dds.stop_event.set()
                await dds_run_task

        return image_url

    async def save_cache_docker_image(self, key: DockerCacheKey, image: str) -> None:
        if (kp := self._config.key_prefix) is not None:
            key = key.append_prefix(kp)

        async with contextlib.AsyncExitStack() as es:
            image_repo: OciRepository = await es.enter_async_context(
                self._image_repo_opener.open_docker_image_repository(image),
            )

            root_image_index = read_oci_repository_root_index(image_repo)
            image_index = get_single_leaf_oci_image_index(root_image_index)

            if self._config.repack:
                prb: OciPackedRepositoryBuilder = es.enter_context(OciPackedRepositoryBuilder(
                    image_repo,
                ))
                built_repo = await asyncio.get_running_loop().run_in_executor(None, prb.build)  # noqa

            else:
                built_repo = build_oci_index_repository(image_index)

            data_server_routes = build_oci_repository_data_server_routes(
                str(key),
                built_repo,
            )

            async def make_file_cache_key(file_path: str) -> str:
                target_cache_key = f'{key!s}--{os.path.basename(file_path).split(".")[0]}'
                await self._data_cache.put_data(
                    target_cache_key,
                    DataCache.FileData(file_path),
                )
                return target_cache_key

            cache_served_manifest = await build_cache_served_docker_image_manifest(
                data_server_routes,
                make_file_cache_key,
            )

        manifest_data = json_dumps_compact(marshal_obj(cache_served_manifest)).encode('utf-8')

        await self._data_cache.put_data(
            str(key),
            DataCache.BytesData(manifest_data),
        )
