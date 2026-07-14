"""
Manual benchmark comparing the reference and closure-compiled interpreter engines over the test corpora. Not run by
pytest - invoke via `python -m omcore.text.abnf.tests.perf`.
"""
import os.path
import time

from ..engines.interp import InterpEngine
from ..meta import parse_grammar


##


def _bench(label: str, gram, src: str, *, reps: int = 10) -> None:
    for eng_label, eng in [
        ('reference', InterpEngine(no_closures=True)),
        ('compiled ', InterpEngine()),
    ]:
        cg = eng.compile(gram)
        m = cg.parse(src)

        t0 = time.perf_counter()
        for _ in range(reps):
            m = cg.parse(src)
        t1 = time.perf_counter()

        print(f'{label} {eng_label}: {(t1 - t0) / reps * 1000:8.2f}ms  ok={m is not None}')


def _main() -> None:
    for name, root, src in [
        (
            'json',
            'JSON-text',
            '{"a": [1, 2.5, -3e4], "b": {"c": true, "d": null}, "e": "some string", "f": [{}, [], "g"]}',
        ),
        (
            'toml',
            'toml',
            'title = "TOML Example"\n\n[owner]\nname = "Tom"\nnums = [ 8000, 8001, 8002 ]\n',
        ),
    ]:
        with open(os.path.join(os.path.dirname(__file__), f'{name}.abnf')) as f:
            gram = parse_grammar(f.read(), root=root)

        _bench(name.ljust(5), gram, src)


if __name__ == '__main__':
    _main()
