from omlish.text.indent import IndentWriter

from ..configs import Items
from ..configs import render


def test_configs():
    conf = Items.of([
        ['user', 'www', 'www'],
        ['worker_processes', '2'],
        ['events', [
            ['worker_connections', '2000'],
        ]],
    ])

    wr = IndentWriter()
    render(wr, conf)
    print(wr.getvalue())
