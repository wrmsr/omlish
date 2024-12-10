from .. import all as ap


class JunkCli(ap.Cli):
    num_runs = 0

    @ap.command(
        ap.arg('foo', metavar='foo'),
        ap.arg('--bar', dest='bar', action='store_true'),
    )
    def run(self) -> None:
        self.num_runs += 1


def test_argparse():
    cli = JunkCli(['run', 'xyz'])
    assert cli.num_runs == 0
    cli()
    assert cli.num_runs == 1
