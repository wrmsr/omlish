# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .cache import DirectoryFileCache
from .cache import FileCache
from .ci import Ci
from .docker.buildcaching import DockerBuildCachingImpl
from .docker.imagepulling import DockerImagePullingImpl
from .docker.inject import bind_docker
from .github.inject import bind_github


##


def bind_ci(
        *,
        config: Ci.Config,

        directory_file_cache_config: ta.Optional[DirectoryFileCache.Config] = None,

        github: bool = False,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [  # noqa
        inj.bind(config),
        inj.bind(Ci, singleton=True),
    ]

    lst.append(bind_docker(
        build_caching_config=DockerBuildCachingImpl.Config(
            service=config.service,

            always_build=config.always_build,
        ),

        image_pulling_config=DockerImagePullingImpl.Config(
            always_pull=config.always_pull,
        ),
    ))

    if directory_file_cache_config is not None:
        lst.extend([
            inj.bind(directory_file_cache_config),
            inj.bind(DirectoryFileCache, singleton=True),
        ])

        if github:
            lst.append(bind_github())
        else:
            lst.append(inj.bind(FileCache, to_key=DirectoryFileCache))

    return inj.as_bindings(*lst)
