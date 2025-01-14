# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import os.path
import shutil
import tarfile
import tempfile
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.contextmanagers import ExitStacked
from omlish.lite.contextmanagers import defer

from .cache import FileCache
from .compose import DockerComposeRun
from .compose import get_compose_service_dependencies
from .dockertars import build_docker_file_hash
from .dockertars import build_docker_tar
from .dockertars import is_docker_image_present
from .dockertars import load_docker_tar
from .dockertars import pull_docker_tar
from .dockertars import read_docker_tar_image_id
from .requirements import build_requirements_hash
from .requirements import download_requirements


class Ci(ExitStacked):
    FILE_NAME_HASH_LEN = 16

    @dc.dataclass(frozen=True)
    class Config:
        project_dir: str

        docker_file: str

        compose_file: str
        service: str

        requirements_txts: ta.Optional[ta.Sequence[str]] = None

        def __post_init__(self) -> None:
            check.not_isinstance(self.requirements_txts, str)

    def __init__(
            self,
            cfg: Config,
            *,
            file_cache: ta.Optional[FileCache] = None,
    ) -> None:
        super().__init__()

        self._cfg = cfg
        self._file_cache = file_cache

    #

    def load_docker_image(self, image: str) -> None:
        if is_docker_image_present(image):
            return

        dep_suffix = image
        for c in '/:.-_':
            dep_suffix = dep_suffix.replace(c, '-')

        tar_file_name = f'docker-{dep_suffix}.tar'

        if self._file_cache is not None and (cache_tar_file := self._file_cache.get_file(tar_file_name)):
            load_docker_tar(cache_tar_file)
            return

        temp_dir = tempfile.mkdtemp()
        with defer(lambda: shutil.rmtree(temp_dir)):
            temp_tar_file = os.path.join(temp_dir, tar_file_name)

            pull_docker_tar(
                image,
                temp_tar_file,
            )

            if self._file_cache is not None:
                self._file_cache.put_file(temp_tar_file)

    @cached_nullary
    def load_compose_service_dependencies(self) -> None:
        deps = get_compose_service_dependencies(
            self._cfg.compose_file,
            self._cfg.service,
        )

        for dep_image in deps.values():
            self.load_docker_image(dep_image)

    #

    @cached_nullary
    def build_ci_image(self) -> str:
        docker_file_hash = build_docker_file_hash(self._cfg.docker_file)[:self.FILE_NAME_HASH_LEN]

        tar_file_name = f'ci-{docker_file_hash}.tar'

        if self._file_cache is not None and (cache_tar_file := self._file_cache.get_file(tar_file_name)):
            image_id = read_docker_tar_image_id(cache_tar_file)
            load_docker_tar(cache_tar_file)
            return image_id

        temp_dir = tempfile.mkdtemp()
        with defer(lambda: shutil.rmtree(temp_dir)):
            temp_tar_file = os.path.join(temp_dir, tar_file_name)

            image_id = build_docker_tar(
                self._cfg.docker_file,
                temp_tar_file,
                cwd=self._cfg.project_dir,
            )

            if self._file_cache is not None:
                self._file_cache.put_file(temp_tar_file)

            return image_id

    #

    @cached_nullary
    def build_requirements_dir(self) -> str:
        requirements_txts = [
            os.path.join(self._cfg.project_dir, rf)
            for rf in check.not_none(self._cfg.requirements_txts)
        ]

        requirements_hash = build_requirements_hash(requirements_txts)[:self.FILE_NAME_HASH_LEN]

        tar_file_name = f'requirements-{requirements_hash}.tar'

        temp_dir = tempfile.mkdtemp()
        self._enter_context(defer(lambda: shutil.rmtree(temp_dir)))  # noqa

        if self._file_cache is not None and (cache_tar_file := self._file_cache.get_file(tar_file_name)):
            with tarfile.open(cache_tar_file) as tar:
                tar.extractall(path=temp_dir)  # noqa

            return temp_dir

        temp_requirements_dir = os.path.join(temp_dir, 'requirements')
        os.makedirs(temp_requirements_dir)

        download_requirements(
            self.build_ci_image(),
            temp_requirements_dir,
            requirements_txts,
        )

        if self._file_cache is not None:
            temp_tar_file = os.path.join(temp_dir, tar_file_name)

            with tarfile.open(temp_tar_file, 'w') as tar:
                for requirement_file in os.listdir(temp_requirements_dir):
                    tar.add(
                        os.path.join(temp_requirements_dir, requirement_file),
                        arcname=requirement_file,
                    )

            self._file_cache.put_file(temp_tar_file)

        return temp_requirements_dir

    #

    def run(self) -> None:
        self.load_compose_service_dependencies()

        ci_image = self.build_ci_image()

        requirements_dir = self.build_requirements_dir()

        #

        setup_cmds = [
            'pip install --root-user-action ignore --find-links /requirements --no-index uv',
            (
                'uv pip install --system --find-links /requirements ' +
                ' '.join(f'-r /project/{rf}' for rf in self._cfg.requirements_txts or [])
            ),
        ]

        #

        test_cmds = [
            '(cd /project && python3 -m pytest -svv test.py)',
        ]

        #

        bash_src = ' && '.join([
            *setup_cmds,
            *test_cmds,
        ])

        with DockerComposeRun(DockerComposeRun.Config(
                compose_file=self._cfg.compose_file,
                service=self._cfg.service,

                image=ci_image,

                run_cmd=['bash', '-c', bash_src],

                run_options=[
                    '-v', f'{os.path.abspath(self._cfg.project_dir)}:/project',
                    '-v', f'{os.path.abspath(requirements_dir)}:/requirements',
                ],

                cwd=self._cfg.project_dir,
        )) as ci_compose_run:
            ci_compose_run.run()
