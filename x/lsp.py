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
"""
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


def _main() -> None:
    config = MultilspyConfig.from_dict({"code_language": "java"})  # Also supports "python", "rust", "csharp"
    logger = MultilspyLogger()
    lsp = JediServer.create(config, logger, os.getcwd())
    with lsp.start_server():
        result = lsp.request_definition


if __name__ == '__main__':
    _main()
