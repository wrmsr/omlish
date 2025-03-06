# @omlish-amalg ../scripts/ci.py
# ruff: noqa: UP006 UP007
"""
Inputs:
 - requirements.txt
 - ci.Dockerfile
 - compose.yml

==

./python -m omdev.ci run --cache-dir omdev/ci/tests/cache omdev/ci/tests/project omlish-ci
"""
import argparse
import asyncio
import itertools
import os.path
import sys
import typing as ta

from omlish.argparse.cli import ArgparseCli
from omlish.argparse.cli import argparse_arg
from omlish.argparse.cli import argparse_cmd
from omlish.lite.check import check
from omlish.lite.inject import inj
from omlish.lite.logs import log
from omlish.logs.standard import configure_standard_logging

from .cache import DirectoryFileCache
from .ci import Ci
from .compose import get_compose_service_dependencies
from .github.bootstrap import is_in_github_actions
from .github.cli import GithubCli
from .inject import bind_ci
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
    async def github(self) -> ta.Optional[int]:
        return await GithubCli(self.unknown_args).async_cli_run()

    #

    DEFAULT_PURGE_MAX_AGE_S = 60 * 60 * 24 * 30
    DEFAULT_PURGE_MAX_SIZE_B = 1024 * 1024 * 1024 * 4

    @argparse_cmd(
        argparse_arg('project-dir'),
        argparse_arg('service'),
        argparse_arg('--docker-file'),
        argparse_arg('--compose-file'),
        argparse_arg('-r', '--requirements-txt', action='append'),

        argparse_arg('--cache-dir'),

        argparse_arg('--no-purge', action='store_true'),

        argparse_arg('--github', action='store_true'),
        argparse_arg('--github-detect', action='store_true'),

        argparse_arg('--cache-served-docker', action='store_true'),

        argparse_arg('--setup-concurrency', type=int),

        argparse_arg('--always-pull', action='store_true'),
        argparse_arg('--always-build', action='store_true'),

        argparse_arg('--no-dependencies', action='store_true'),

        argparse_arg('--setup-only', action='store_true'),

        argparse_arg('-e', '--env', action='append'),
        argparse_arg('-v', '--volume', action='append'),

        argparse_arg('cmd', nargs=argparse.REMAINDER),
    )
    async def run(self) -> None:
        project_dir = self.args.project_dir
        docker_file = self.args.docker_file
        compose_file = self.args.compose_file
        requirements_txts = self.args.requirements_txt
        cache_dir = self.args.cache_dir

        #

        cmd = ' '.join(self.args.cmd)
        check.non_empty_str(cmd)

        #

        check.state(os.path.isdir(project_dir))

        #

        def find_alt_file(*alts: str) -> ta.Optional[str]:
            for alt in alts:
                alt_file = os.path.abspath(os.path.join(project_dir, alt))
                if os.path.isfile(alt_file):
                    log.debug('Using %s', alt_file)
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
            compose_file = find_alt_file(*[
                f'{f}.{x}'
                for f in [
                    'docker/docker-compose',
                    'docker/compose',
                    'docker-compose',
                    'compose',
                ]
                for x in ['yaml', 'yml']
            ])
        check.state(os.path.isfile(compose_file))

        if not requirements_txts:
            requirements_txts = []
            for rf in [
                'requirements.txt',
                'requirements-dev.txt',
                'requirements-ci.txt',
            ]:
                if os.path.exists(os.path.join(project_dir, rf)):
                    log.debug('Using %s', rf)
                    requirements_txts.append(rf)
        else:
            for rf in requirements_txts:
                check.state(os.path.isfile(rf))

        #

        github = self.args.github
        if not github and self.args.github_detect:
            github = is_in_github_actions()
            if github:
                log.debug('Github detected')

        #

        if cache_dir is not None:
            cache_dir = os.path.abspath(cache_dir)
            log.debug('Using cache dir %s', cache_dir)

        #

        run_options: ta.List[str] = []
        for run_arg, run_arg_vals in [
            ('-e', self.args.env or []),
            ('-v', self.args.volume or []),
        ]:
            run_options.extend(itertools.chain.from_iterable(
                [run_arg, run_arg_val]
                for run_arg_val in run_arg_vals
            ))

        #

        config = Ci.Config(
            project_dir=project_dir,

            docker_file=docker_file,

            compose_file=compose_file,
            service=self.args.service,

            requirements_txts=requirements_txts,

            cmd=ShellCmd(cmd),

            always_pull=self.args.always_pull,
            always_build=self.args.always_build,

            setup_concurrency=self.args.setup_concurrency,

            no_dependencies=self.args.no_dependencies,

            setup_only=self.args.setup_only,

            run_options=run_options,
        )

        directory_file_cache_config: ta.Optional[DirectoryFileCache.Config] = None
        if cache_dir is not None:
            directory_file_cache_config = DirectoryFileCache.Config(
                dir=cache_dir,

                no_purge=bool(self.args.no_purge),

                purge_max_age_s=self.DEFAULT_PURGE_MAX_AGE_S,
                purge_max_size_b=self.DEFAULT_PURGE_MAX_SIZE_B,
            )

        injector = inj.create_injector(bind_ci(
            config=config,

            directory_file_cache_config=directory_file_cache_config,

            github=github,

            cache_served_docker=self.args.cache_served_docker,
        ))

        async with injector[Ci] as ci:
            await ci.run()

        if directory_file_cache_config is not None and not directory_file_cache_config.no_purge:
            dfc = injector[DirectoryFileCache]
            dfc.purge()


async def _async_main() -> ta.Optional[int]:
    return await CiCli().async_cli_run()


def _main() -> None:
    configure_standard_logging('DEBUG')

    sys.exit(rc if isinstance(rc := asyncio.run(_async_main()), int) else 0)


if __name__ == '__main__':
    _main()
