import textwrap

import tree_sitter as ts
import tree_sitter_python as ts_py


def _main() -> None:
    py_language = ts.Language(ts_py.language())

    parser = ts.Parser(py_language)

    tree = parser.parse(textwrap.dedent("""
        def foo():
            if bar:
                baz()
    """).encode('utf-8'))

    print(tree)
    print(tree.root_node)


if __name__ == '__main__':
    _main()
