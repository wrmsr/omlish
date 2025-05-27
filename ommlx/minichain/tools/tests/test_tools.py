import json
import typing as ta

from ..jsonschema import ToolJsonschemaRenderer
from ..reflection import ToolReflector


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
        q_s: A sequence of strings. This is a long docstring to test word wrapping. This is a long docstring to test
            word wrapping. This is a long docstring to test word wrapping. This is a long docstring to test word
            wrapping. This is a long docstring to test word wrapping. This is a long docstring to test word wrapping.
            This is a long docstring to test word wrapping.
        o_q_s: An *optional* sequence of strings

    Returns:
        The foo'd params.
    """

    return repr((i, s, lit, q_s, o_q_s))


def test_reflection():
    ts = ToolReflector().make_function(foo)
    print(ts)

    js = ToolJsonschemaRenderer().render_tool(ts)
    print(json.dumps(js, indent=2, separators=(', ', ': ')))

    assert js == {
        'name': 'foo',
        'description': "Foo's some params.\n",
        'parameters': {
            'type': 'object',
            'properties': {
                'i': {
                    'description': 'Some int',
                    'type': 'integer',
                },
                's': {
                    'description': 'A string',
                    'type': 'string',
                },
                'lit': {
                    'description': 'A literal of some kind',
                    'type': 'string',
                    'enum': [
                        'foo',
                        'bar',
                    ],
                },
                'q_s': {
                    'description': (
                        'A sequence of strings. This is a long docstring to test word wrapping. This is a long '
                        'docstring to test\nword wrapping. This is a long docstring to test word wrapping. This is a '
                        'long docstring to test word\nwrapping. This is a long docstring to test word wrapping. This '
                        'is a long docstring to test word wrapping.\nThis is a long docstring to test word wrapping.'
                    ),
                    'type': 'array',
                    'items': {
                        'type': 'string',
                    },
                },
                'o_q_s': {
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
            'additionalProperties': False,
        },
        'return': {
            'description': "The foo'd params.",
            'type': {
                'type': 'string',
            },
        },
    }
