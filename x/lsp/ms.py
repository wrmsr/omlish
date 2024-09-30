"""
.venv/bin/pip install --no-deps git+https://github.com/microsoft/multilspy

https://stackoverflow.com/a/77482983
https://github.com/microsoft/monitors4codegen#4-multilspy

!! https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/

https://github.com/python-lsp/python-lsp-server

https://github.com/pappasam/jedi-language-server
https://github.com/DetachHead/basedpyright
https://github.com/mtshiba/pylyzer

https://github.com/microsoft/pyright/blob/main/docs/mypy-comparison.md

https://github.com/jecki/ts2python
https://github.com/predragnikolic/OLSP
"""
import asyncio
import os

from multilspy.multilspy_logger import MultilspyLogger
from multilspy.language_server import LanguageServer
from multilspy.lsp_protocol_handler.server import ProcessLaunchInfo
from multilspy.multilspy_config import MultilspyConfig


class JediServer(LanguageServer):
    def __init__(
            self,
            config: MultilspyConfig,
            logger: MultilspyLogger,
            repository_root_path: str,
    ) -> None:
        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(
                cmd='jedi-language-server',
                cwd=repository_root_path,
            ),
            'python',
        )


async def _main() -> None:
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    os.chdir(root_dir)

    config = MultilspyConfig.from_dict({
        "code_language": "python",  # Also supports "python", "rust", "csharp"
        "trace_lsp_communication": True,
    })
    logger = MultilspyLogger()
    lsp = JediServer.create(config, logger, root_dir)

    async with lsp.start_server():
        result = await lsp.request_definition(os.path.relpath(__file__, root_dir), 25, 17)
        print(result)


if __name__ == '__main__':
    asyncio.run(_main())
