import dataclasses as dc
import inspect  # noqa
import os
import resource
import time

import pytest

from ... import dataclasses as odc


@pytest.mark.skip()
def test_perf():
    @dc.dataclass()
    class CBuiltin:
        x: int

    class CStandard(odc.Data):
        x: int

    class CDict(
        odc.Data,
        aspects=odc.process.replace_aspects(odc.process.DEFAULT_ASPECTS, odc.process.dicts.ASPECT_REPLACEMENTS),
    ):
        x: int

    @dc.dataclass(frozen=True)
    class CBuiltinFrozen:
        x: int

    class CFrozen(odc.Frozen):
        x: int

    class CPure(odc.Pure):
        x: int

    class CTuple(odc.Tuple):
        x: int

    print()

    for C in [
        CBuiltin,
        CStandard,
        CDict,
        CBuiltinFrozen,
        CFrozen,
        CPure,
        CTuple,
    ]:
        print(C)

        c = C(1)
        assert c.x == 1

        start = time.time()
        for _ in range(1_000_000):
            c = C(1)
        end = time.time()
        print(f'new: {end - start:0.04}')

        start = time.time()
        for _ in range(10_000_000):
            c.x  # noqa
        end = time.time()
        print(f'getattr: {end - start:0.04}')

        try:
            c.x = 2
        except Exception:  # noqa
            pass
        else:
            start = time.time()
            for i in range(10_000_000):
                c.x = i  # noqa
            end = time.time()
            print(f'setattr: {end - start:0.04}')

        getrss = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        start = getrss()
        r, w = os.pipe()
        pid = os.fork()
        if not pid:
            os.close(r)
            l = [C(1) for _ in range(2_000_000)]  # noqa
            end = getrss()
            os.write(w, f'{end}\n'.encode('utf-8'))
            os.close(w)
            os._exit(0)
        else:
            os.close(w)
            with os.fdopen(r) as rf:
                end = int(rf.readline())
            os.waitpid(pid, 0)
        print(f'rss: {end - start:,}')

        print()
