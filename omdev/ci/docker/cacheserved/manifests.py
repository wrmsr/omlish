# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.check import check

from ....dataserver.routes import DataServerRoute
from ....dataserver.targets import BytesDataServerTarget
from ....dataserver.targets import DataServerTarget
from ....dataserver.targets import FileDataServerTarget


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
