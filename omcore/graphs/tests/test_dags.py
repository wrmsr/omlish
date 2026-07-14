import pytest

from ..dags import Dag
from ..dags import LinkError
from ..dags import invert_links
from ..dags import traverse_links


def test_traverse_links():
    assert traverse_links(
        {
            'A': 'BC',
            'B': 'CD',
        },
        'A',
    ) == set('BCD')

    assert traverse_links(
        {
            'A': 'BC',
            'B': 'CD',
        },
        'A',
        include_roots=True,
    ) == set('ABCD')

    assert traverse_links(
        {
            'A': 'BC',
            'B': 'CD',
        },
        'B',
    ) == set('CD')

    with pytest.raises(LinkError):
        traverse_links(
            {
                'A': 'BC',
                'B': 'CD',
            },
            'A',
            strict=True,
        )

    assert traverse_links(
        {
            'A': 'BC',
            'B': 'CD',
            'C': '',
            'D': '',
        },
        'A',
        strict=True,
    ) == set('BCD')

    assert traverse_links(
        {
            'A': 'BC',
            'B': 'CD',
            'C': '',
            'D': 'A',
        },
        'A',
    ) == set('BCD')

    assert traverse_links(
        {
            'A': 'BC',
            'B': 'CD',
            'C': '',
            'D': 'A',
        },
        'A',
        include_roots=True,
    ) == set('ABCD')


def test_invert_links():
    for ia in (None, 'add'):
        assert invert_links(
            {
                'A': 'BC',
                'B': 'CD',
            },
            **(dict(if_absent=ia) if ia is not None else {}),  # type: ignore[arg-type]
        ) == {
            'B': set('A'),
            'C': set('AB'),
            'D': set('B'),
        }

    assert invert_links(
        {
            'A': 'BC',
            'B': 'CD',
        },
        auto_add_roots=True,
        if_absent='ignore',
    ) == {
        'A': set(),
        'B': set('A'),
    }

    with pytest.raises(LinkError):
        invert_links(
            {
                'A': 'BC',
                'B': 'CD',
            },
            auto_add_roots=True,
            if_absent='raise',
        )

    assert invert_links(
        {
            'A': 'BC',
            'B': 'CD',
            'C': '',
            'D': '',
        },
        auto_add_roots=True,
        if_absent='raise',
    ) == {
        'A': set(),
        'B': set('A'),
        'C': set('AB'),
        'D': set('B'),
    }


def test_dag():
    dag = Dag({
        'A': 'BC',
        'B': 'CD',
        'C': '',
        'D': '',
    })

    assert dag.input_sets_by_output == {
        'A': set('BC'),
        'B': set('CD'),
        'C': set(''),
        'D': set(''),
    }

    assert dag.output_sets_by_input == {
        'A': set(''),
        'B': set('A'),
        'C': set('AB'),
        'D': set('B'),
    }

    subdag = dag.subdag('B')
    assert subdag.roots == set('B')
    assert subdag.inputs == set('CD')
    assert subdag.outputs == set('A')
    assert subdag.output_inputs == set('BCD')
    assert subdag.all == set('ABCD')


def test_dag2():
    dag = Dag({
        '*': 'AE',

        'A': 'BC',
        'B': 'CD',
        'C': '',
        'D': '',

        'E': 'FG',
        'F': 'GH',
        'G': '',
        'H': '',
    })

    assert dag.output_sets_by_input == {
        '*': set(),

        'A': set('*'),
        'B': set('A'),
        'C': set('AB'),
        'D': set('B'),

        'E': set('*'),
        'F': set('E'),
        'G': set('EF'),
        'H': set('F'),
    }

    subdag = dag.subdag('B')
    assert subdag.roots == set('B')
    assert subdag.inputs == set('CD')
    assert subdag.outputs == set('*A')
    assert subdag.output_inputs == set('BCDEFGH')
    assert subdag.all == set(dag.input_sets_by_output)

    subdag = dag.subdag('B', ignored='*')
    assert subdag.roots == set('B')
    assert subdag.inputs == set('CD')
    assert subdag.outputs == set('A')
    assert subdag.output_inputs == set('BCD')
    assert subdag.all == set('ABCD')
