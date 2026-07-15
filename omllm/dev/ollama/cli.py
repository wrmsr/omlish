from omcore import check
from omcore.argparse import all as ap
from omcore.formats.json import all as json
from omcore.http import all as http
from omcore.logs import all as logs
from omdev.cli import CliModule


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


# @om-manifest
_CLI_MODULE = CliModule('ollama', __name__)


if __name__ == '__main__':
    _main()
