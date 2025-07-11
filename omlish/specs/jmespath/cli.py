import argparse
import dataclasses as dc
import sys
import typing as ta

from ...formats import json
from .ast import Node
from .errors import ArityError
from .errors import JmespathTypeError
from .errors import JmespathValueError
from .errors import ParseError
from .errors import UnknownFunctionError
from .parser import compile  # noqa
from .parser import search
from .visitor import node_type


##


def _ast_to_json(o: ta.Any) -> ta.Any:
    if isinstance(o, json.SCALAR_TYPES):
        return o
    elif isinstance(o, Node):
        return {node_type(o): {f.name: _ast_to_json(getattr(o, f.name)) for f in dc.fields(o)}}
    elif isinstance(o, (list, tuple)):
        return [_ast_to_json(e) for e in o]
    else:
        raise TypeError(o)


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('expression')
    parser.add_argument('-f', '--filename')
    parser.add_argument('-c', '--compact', action='store_true')
    parser.add_argument('--ast', action='store_true')
    args = parser.parse_args()

    if args.compact:
        json_dumps = json.dumps_compact
    else:
        json_dumps = json.dumps_pretty

    expression = args.expression
    if args.ast:
        expression = compile(args.expression)
        print(json_dumps(_ast_to_json(expression.parsed)))
        return 0

    if args.filename:
        with open(args.filename) as f:
            data = json.load(f)
    else:
        data = sys.stdin.read()
        data = json.loads(data)

    try:
        print(json_dumps(search(expression, data)))
        return 0

    except ArityError as e:
        print(f'invalid-arity: {e}', file=sys.stderr)
        return 1

    except JmespathTypeError as e:
        print(f'invalid-type: {e}', file=sys.stderr)
        return 1

    except JmespathValueError as e:
        print(f'invalid-value: {e}', file=sys.stderr)
        return 1

    except UnknownFunctionError as e:
        print(f'unknown-function: {e}', file=sys.stderr)
        return 1

    except ParseError as e:
        print(f'syntax-error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(_main())
