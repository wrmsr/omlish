"""
https://github.com/tomnomnom/gron
https://github.com/tomnomnom/gron/pull/42
https://github.com/adamritter/fastgron
"""
import json
import typing as ta

from omlish import check


DOC = {
    "name": "Example Document",
    "version": 1.0,
    "active": True,
    "tags": ["test", "json", "example"],
    "metadata": {
        "author": "Alice Smith",
        "created": "2025-05-10T15:00:00Z",
        "license": None,
    },
    "items": [
        {
            "id": 1,
            "name": "Widget A",
            "price": 19.99,
            "dimensions": {
                "width": 5.5,
                "height": 7.0,
                "depth": 2.3,
            },
            "tags": ["sale", "popular"],
        },
        {
            "id": 2,
            "name": "Widget B",
            "price": 29.99,
            "dimensions": {
                "width": 6.0,
                "height": 8.5,
                "depth": 2.0,
            },
            "tags": [],
        }
    ],
    "config": {
        "debug": False,
        "threshold": 0.75,
        "features": {
            "beta": True,
            "experimental": ["x1", "x2"],
        },
    },
}


def print_obj(
        obj,
        *,
        prefix='json',
        try_dot_members=False,
):
    def rec(cur, pfx):
        if isinstance(cur, dict):
            print(f'{pfx} = {{}};')
            for k, v in cur.items():
                dk = json.dumps(k)
                if try_dot_members and (k == dk):
                    rec(v, f'{pfx}.{dk}')
                else:
                    rec(v, f'{pfx}[{dk}]')

        elif isinstance(cur, list):
            print(f'{pfx} = [];')
            for i, e in enumerate(cur):
                rec(e, f'{pfx}[{i}]')

        else:
            print(f'{pfx} = {json.dumps(cur)};')

    rec(obj, prefix)


def build_jgron(
        root,
        *,
        share_paths: bool = False,
):
    stack = [(None, root)]
    path = []
    while stack:
        ic, obj = stack[-1]

        if ic is None:
            stack.pop()

            yp: ta.Sequence
            if not share_paths:
                yp = tuple(path)
            else:
                yp = path

            if isinstance(obj, dict):
                yield (yp, {})
                stack.append((dict, iter(obj.items())))

            elif isinstance(obj, list):
                yield (yp, [])
                stack.append((list, enumerate(obj)))

            else:
                yield (yp, obj)
                if stack and stack[-1][0] is not None:
                    path.pop()

        elif ic in (list, dict):
            try:
                kv = next(obj)

            except StopIteration:
                stack.pop()
                if stack and stack[-1][0] is not None:
                    path.pop()

            else:
                k, v = kv
                path.append(k)
                stack.append((None, v))

        else:
            raise TypeError(ic)

    check.empty(path)


def unbuild_jgron(items):
    stack = []
    lp: ta.Sequence | None = None
    for path, val in items:
        while lp is not None and (len(lp) > len(path) or (len(lp) == len(path) and lp[-1] != path[-1])):
            stack.pop()
            lp.pop()  # noqa

        if stack:
            pv = stack[-1]

            if isinstance(pv, list):
                check.state(len(path) == len(lp) + 1)
                [*xp, i] = path
                check.state(xp == lp)
                check.equal(len(pv), i)

            elif isinstance(pv, dict):
                check.state(len(path) == len(lp) + 1)
                [*xp, k] = path
                check.state(xp == lp)
                check.not_in(k, pv)

            else:
                raise TypeError(pv)

        else:
            pv = None

        if isinstance(val, (dict, list)):
            check.empty(val)
            if not path:
                check.state(lp is None)
                lp = []
            else:
                check.state(len(path) == len(lp) + 1)
                lp.append(path[-1])  # noqa
            nxt_val = type(val)()
            stack.append(nxt_val)
            val = nxt_val

        if isinstance(pv, list):
            pv.append(val)

        elif isinstance(pv, dict):
            pv[path[-1]] = val

        elif pv is not None:
            raise TypeError(pv)

    if lp is not None:
        check.not_empty(stack)
        yield stack[0]

    else:
        check.empty(stack)


def _main() -> None:
    print(json.dumps(DOC, indent=None, separators=(',', ':')))
    print()

    print_obj(DOC)
    print()

    jgl = list(build_jgron(DOC))
    for jg in jgl:
        print(json.dumps(jg, indent=None, separators=(',', ':')))
    print()

    print(json.dumps(list(unbuild_jgron(jgl)), indent=None, separators=(',', ':')))
    print()


if __name__ == '__main__':
    _main()
