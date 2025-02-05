# ruff: noqa: PT009
import contextlib
import os.path
import unittest

from omlish.os.temp import temp_dir_context

from ..ci import Ci
from ..shell import ShellCmd


class TestCi(unittest.IsolatedAsyncioTestCase):
    async def test_ci(self):
        async with contextlib.AsyncExitStack() as es:
            self_dir = os.path.dirname(__file__)
            project_dir = os.path.join(self_dir, 'project')
            temp_dir: str = es.enter_context(temp_dir_context())  # noqa

            async with Ci(Ci.Config(
                    project_dir=project_dir,

                    docker_file=os.path.join(project_dir, 'Dockerfile'),

                    compose_file=os.path.join(project_dir, 'compose.yml'),
                    service='omlish-ci',

                    cmd=ShellCmd('true'),

                    requirements_txts=[
                        'requirements-dev.txt',
                        'requirements.txt',
                    ],
            )) as ci:
                await ci.run()
