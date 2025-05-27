import json
import typing as ta

from ..reflection import Reflector
from ..rendering import Renderer


def test_reflection():
    def foo(
            i: int,
            s: str,
            lit: ta.Literal['foo', 'bar'],
            q_s: ta.Sequence[str],
            o_q_s: ta.Sequence[str] | None = None,
    ) -> str:
        """
        Foo's some params.

        Args:
            i: Some int
            s: A string
            lit: A literal of some kind
            q_s: A sequence of strings
            o_q_s: An *optional* sequence of strings

        Returns:
            The foo'd params.
        """

        return repr((i, s, lit, q_s, o_q_s))

    fn = Reflector().make_function(foo)
    print(fn)

    rf = Renderer().render_function(fn)
    print(json.dumps(rf, indent=2, separators=(', ', ': ')))

    assert rf == {
        'type': 'function',
        'function': {
            'name': 'foo',
            'description': "Foo's some params.\n",
            'parameters': {
                'type': 'object',
                'properties': {
                    'i': {
                        'name': 'i',
                        'description': 'Some int',
                        'type': 'integer',
                    },
                    's': {
                        'name': 's',
                        'description': 'A string',
                        'type': 'string',
                    },
                    'lit': {
                        'name': 'lit',
                        'description': 'A literal of some kind',
                        'type': 'string',
                        'enum': [
                            'foo',
                            'bar',
                        ],
                    },
                    'q_s': {
                        'name': 'q_s',
                        'description': 'A sequence of strings',
                        'type': 'array',
                        'items': {
                            'type': 'string',
                        },
                    },
                    'o_q_s': {
                        'name': 'o_q_s',
                        'description': 'An *optional* sequence of strings',
                        'type': 'array',
                        'items': {
                            'type': 'string',
                        },
                        'nullable': True,
                    },
                },
                'required': [
                    'i',
                    's',
                    'lit',
                    'q_s',
                ],
            },
            'return': {
                'description': "The foo'd params.",
                'type': {
                    'type': 'string',
                },
            },
        },
    }
