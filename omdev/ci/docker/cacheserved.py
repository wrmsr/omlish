# ruff: noqa: UP006 UP007
import abc
import asyncio
import contextlib
import dataclasses as dc
import json
import os.path
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.check import check
from omlish.lite.json import json_dumps_compact
from omlish.lite.logs import log
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj

from ...dataserver.routes import DataServerRoute
from ...dataserver.server import DataServer
from ...dataserver.targets import BytesDataServerTarget
from ...dataserver.targets import DataServerTarget
from ...dataserver.targets import FileDataServerTarget
from ...oci.building import build_oci_index_repository
from ...oci.data import get_single_leaf_oci_image_index
from ...oci.dataserver import build_oci_repository_data_server_routes
from ...oci.loading import read_oci_repository_root_index
from ...oci.pack.repositories import OciPackedRepositoryBuilder
from ...oci.repositories import OciRepository
from ..cache import DataCache
from ..cache import read_data_cache_data
from .cache import DockerCache
from .dataserver import DockerDataServer
from .repositories import DockerImageRepositoryOpener


##


@dc.dataclass(frozen=True)
class CacheServedDockerImageManifest:
    @dc.dataclass(frozen=True)
    class Route:
        paths: ta.Sequence[str]

        content_type: str
        content_length: int

        @dc.dataclass(frozen=True)
        class Target(abc.ABC):  # noqa
            pass

        @dc.dataclass(frozen=True)
        class BytesTarget(Target):
            data: bytes

        @dc.dataclass(frozen=True)
        class CacheKeyTarget(Target):
            key: str

        target: Target

        def __post_init__(self) -> None:
            check.not_isinstance(self.paths, str)

    routes: ta.Sequence[Route]


#


async def build_cache_served_docker_image_manifest(
        data_server_routes: ta.Iterable[DataServerRoute],
        make_file_cache_key: ta.Callable[[str], ta.Awaitable[str]],
) -> CacheServedDockerImageManifest:
    routes: ta.List[CacheServedDockerImageManifest.Route] = []

    for data_server_route in data_server_routes:
        content_length: int

        data_server_target = data_server_route.target
        target: CacheServedDockerImageManifest.Route.Target
        if isinstance(data_server_target, BytesDataServerTarget):
            bytes_data = check.isinstance(data_server_target.data, bytes)
            content_length = len(bytes_data)
            target = CacheServedDockerImageManifest.Route.BytesTarget(bytes_data)

        elif isinstance(data_server_target, FileDataServerTarget):
            file_path = check.non_empty_str(data_server_target.file_path)
            content_length = os.path.getsize(file_path)
            cache_key = await make_file_cache_key(file_path)
            target = CacheServedDockerImageManifest.Route.CacheKeyTarget(cache_key)

        else:
            raise TypeError(data_server_target)

        routes.append(CacheServedDockerImageManifest.Route(
            paths=data_server_route.paths,

            content_type=check.non_empty_str(data_server_target.content_type),
            content_length=content_length,

            target=target,
        ))

    return CacheServedDockerImageManifest(
        routes=routes,
    )


#


async def build_cache_served_docker_image_data_server_routes(
        manifest: CacheServedDockerImageManifest,
        make_cache_key_target: ta.Callable[..., ta.Awaitable[DataServerTarget]],
) -> ta.List[DataServerRoute]:
    routes: ta.List[DataServerRoute] = []

    for manifest_route in manifest.routes:
        manifest_target = manifest_route.target

        target_kwargs: dict = dict(
            content_type=manifest_route.content_type,
            content_length=manifest_route.content_length,
        )

        target: DataServerTarget

        if isinstance(manifest_target, CacheServedDockerImageManifest.Route.BytesTarget):
            target = DataServerTarget.of(manifest_target.data, **target_kwargs)

        elif isinstance(manifest_target, CacheServedDockerImageManifest.Route.CacheKeyTarget):
            target = await make_cache_key_target(manifest_target.key, **target_kwargs)

        else:
            raise TypeError(manifest_target)

        routes.append(DataServerRoute(
            paths=manifest_route.paths,
            target=target,
        ))

    return routes


##


class CacheServedDockerCache(DockerCache):
    @dc.dataclass(frozen=True)
    class Config:
        port: int = 5021

        repack: bool = True

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

    async def load_cache_docker_image(self, key: str) -> ta.Optional[str]:
        if (manifest_data := await self._data_cache.get_data(key)) is None:
            return None

        manifest_bytes = await read_data_cache_data(manifest_data)

        manifest: CacheServedDockerImageManifest = unmarshal_obj(
            json.loads(manifest_bytes.decode('utf-8')),
            CacheServedDockerImageManifest,
        )

        async def make_cache_key_target(target_cache_key: str, **target_kwargs: ta.Any) -> DataServerTarget:  # noqa
            # FIXME: url
            cache_data = check.not_none(await self._data_cache.get_data(target_cache_key))
            file_path = check.isinstance(cache_data, DataCache.FileData).file_path
            return DataServerTarget.of(
                file_path=file_path,
                **target_kwargs,
            )

        data_server_routes = await build_cache_served_docker_image_data_server_routes(
            manifest,
            make_cache_key_target,
        )

        data_server = DataServer(DataServer.HandlerRoute.of_(*data_server_routes))

        image_url = f'localhost:{self._config.port}/{key}'

        async with DockerDataServer(
                self._config.port,
                data_server,
                handler_log=log,
        ) as dds:
            dds_run_task = asyncio.create_task(dds.run())
            try:
                # FIXME: lol
                await asyncio.sleep(3.)

                await asyncio_subprocesses.check_call(
                    'docker',
                    'pull',
                    image_url,
                )

            finally:
                dds.stop_event.set()
                await dds_run_task

        return image_url

    async def save_cache_docker_image(self, key: str, image: str) -> None:
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
                built_repo = await asyncio.get_running_loop().run_in_executor(None, prb.build)

            else:
                built_repo = build_oci_index_repository(image_index)

            data_server_routes = build_oci_repository_data_server_routes(
                key,
                built_repo,
            )

            async def make_file_cache_key(file_path: str) -> str:
                target_cache_key = f'{key}--{os.path.basename(file_path).split(".")[0]}'
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
            key,
            DataCache.BytesData(manifest_data),
        )
