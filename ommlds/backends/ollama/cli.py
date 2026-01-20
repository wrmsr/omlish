from omdev.cli import CliModule
from omlish import check
from omlish.argparse import all as ap
from omlish.formats import json
from omlish.http import all as http
from omlish.logs import all as logs


log = logs.get_module_logger(globals())


##


class Cli(ap.Cli):
    @ap.cmd()
    def list(self) -> None:
        resp = http.request('http://localhost:11434/api/tags', check=True)
        data = json.loads(check.not_none(resp.data).decode('utf-8'))
        print(json.dumps_pretty(data))


##


def _main() -> None:
    logs.configure_standard_logging('INFO')
    Cli()()


# @omlish-manifest
_CLI_MODULE = CliModule('ollama', __name__)


if __name__ == '__main__':
    _main()
