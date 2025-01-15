# @omlish-amalg ../scripts/ci.py
# ruff: noqa: UP006 UP007
# @omlish-lite
"""
Inputs:
 - requirements.txt
 - ci.Dockerfile
 - compose.yml

==

./python -m ci run --cache-dir ci/cache ci/project omlish-ci
"""
import asyncio
import os.path
import sys
import typing as ta

from omlish.argparse.cli import ArgparseCli
from omlish.argparse.cli import argparse_arg
from omlish.argparse.cli import argparse_cmd
from omlish.lite.check import check
from omlish.logs.standard import configure_standard_logging

from .cache import DirectoryFileCache
from .cache import DirectoryShellCache
from .cache import ShellCache
from .ci import Ci
from .compose import get_compose_service_dependencies
from .github.cli import GithubCli
from .requirements import build_requirements_hash
from .shell import ShellCmd


class CiCli(ArgparseCli):
    #

    @argparse_cmd(
        argparse_arg('requirements-txt', nargs='+'),
    )
    def print_requirements_hash(self) -> None:
        requirements_txts = self.args.requirements_txt

        print(build_requirements_hash(requirements_txts))

    #

    @argparse_cmd(
        argparse_arg('compose-file'),
        argparse_arg('service'),
    )
    def dump_compose_deps(self) -> None:
        compose_file = self.args.compose_file
        service = self.args.service

        print(get_compose_service_dependencies(
            compose_file,
            service,
        ))

    #

    @argparse_cmd(
        accepts_unknown=True,
    )
    def github(self) -> ta.Optional[int]:
        return GithubCli(self.unknown_args).cli_run()

    #

    @argparse_cmd(
        argparse_arg('project-dir'),
        argparse_arg('service'),
        argparse_arg('--docker-file'),
        argparse_arg('--compose-file'),
        argparse_arg('-r', '--requirements-txt', action='append'),
        argparse_arg('--cache-dir'),
    )
    async def run(self) -> None:
        project_dir = self.args.project_dir
        docker_file = self.args.docker_file
        compose_file = self.args.compose_file
        service = self.args.service
        requirements_txts = self.args.requirements_txt
        cache_dir = self.args.cache_dir

        #

        check.state(os.path.isdir(project_dir))

        #

        def find_alt_file(*alts: str) -> ta.Optional[str]:
            for alt in alts:
                alt_file = os.path.abspath(os.path.join(project_dir, alt))
                if os.path.isfile(alt_file):
                    return alt_file
            return None

        if docker_file is None:
            docker_file = find_alt_file(
                'docker/ci/Dockerfile',
                'docker/ci.Dockerfile',
                'ci.Dockerfile',
                'Dockerfile',
            )
        check.state(os.path.isfile(docker_file))

        if compose_file is None:
            compose_file = find_alt_file(
                'docker/compose.yml',
                'compose.yml',
            )
        check.state(os.path.isfile(compose_file))

        if not requirements_txts:
            requirements_txts = []
            for rf in [
                'requirements.txt',
                'requirements-dev.txt',
                'requirements-ci.txt',
            ]:
                if os.path.exists(os.path.join(project_dir, rf)):
                    requirements_txts.append(rf)
        else:
            for rf in requirements_txts:
                check.state(os.path.isfile(rf))

        #

        shell_cache: ta.Optional[ShellCache] = None
        if cache_dir is not None:
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            check.state(os.path.isdir(cache_dir))
            directory_file_cache = DirectoryFileCache(cache_dir)
            shell_cache = DirectoryShellCache(directory_file_cache)

        #

        with Ci(
                Ci.Config(
                    project_dir=project_dir,
                    docker_file=docker_file,
                    compose_file=compose_file,
                    service=service,
                    requirements_txts=requirements_txts,

                    cmd=ShellCmd('cd /project && python3 -m pytest -svv test.py'),
                ),
                shell_cache=shell_cache,
        ) as ci:
            ci.run()


async def _async_main() -> ta.Optional[int]:
    return await CiCli().async_cli_run()


def _main() -> None:
    configure_standard_logging('DEBUG')

    sys.exit(rc if isinstance(rc := asyncio.run(_async_main()), int) else 0)


if __name__ == '__main__':
    _main()
