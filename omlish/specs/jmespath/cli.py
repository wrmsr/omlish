#!/usr/bin/env python3
import argparse
import sys

from ...formats import json
from .ast import Node
from .exceptions import ArityError
from .exceptions import JmespathTypeError
from .exceptions import JmespathValueError
from .exceptions import ParseError
from .exceptions import UnknownFunctionError
from .parser import compile
from .parser import search


def _node_dict(n: Node) -> dict:
    raise NotImplementedError


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
        print(json_dumps(expression.parsed))
        return 0

    if args.filename:
        with open(args.filename) as f:
            data = json.load(f)
    else:
        data = sys.stdin.read()
        data = json.loads(data)

    try:
        print(json_dumps(search(expression, data), ensure_ascii=False))
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
