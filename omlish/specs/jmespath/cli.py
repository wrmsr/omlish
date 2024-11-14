#!/usr/bin/env python3
import argparse
import sys

from ...formats import json
from . import exceptions
from .parser import compile
from .parser import search


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

    except exceptions.ArityError as e:
        print(f'invalid-arity: {e}', file=sys.stderr)
        return 1

    except exceptions.JmespathTypeError as e:
        print(f'invalid-type: {e}', file=sys.stderr)
        return 1

    except exceptions.JmespathValueError as e:
        print(f'invalid-value: {e}', file=sys.stderr)
        return 1

    except exceptions.UnknownFunctionError as e:
        print(f'unknown-function: {e}', file=sys.stderr)
        return 1

    except exceptions.ParseError as e:
        print(f'syntax-error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(_main())
