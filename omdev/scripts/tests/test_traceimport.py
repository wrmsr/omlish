import dataclasses as dc
import json
import typing as ta

from .. import traceimport as ti


def test_traceimport():
    columns = [
        ('root_id', 'int'),
        ('parent_id', 'int'),
    ]

    for f in dc.fields(ti.Node):
        if f.type in (str, ta.Optional[str]):
            columns.append((f.name, 'text'))
        elif f.type in (int, ta.Optional[int]):
            columns.append((f.name, 'int'))
        elif f.name == 'children':
            continue
        elif f.type in (ti.Stats, ta.Optional[ti.Stats]):
            pfx = f.name[:-5] if f.name != 'stats' else ''
            columns.extend([
                (pfx + 'time', 'real'),
                (pfx + 'vm_rss', 'int'),
                (pfx + 'vm_vms', 'int'),
            ])
        else:
            columns.append((f.name, 'text'))

    import pprint
    pprint.pprint(columns)

    n = ti.Node()

    dct = {}
    for f in dc.fields(ti.Node):
        v = getattr(n, f.name)
        if f.type in (str, ta.Optional[str], int, ta.Optional[int]):
            dct[f.name] = v
        elif f.name == 'children':
            continue
        elif f.type in (ti.Stats, ta.Optional[ti.Stats]):
            pfx = f.name[:-5] if f.name != 'stats' else ''
            dct.update((pfx + a, getattr(v, a)) for a in ti.Stats.ATTRS)
        else:
            dct[f.name] = json.dumps(indent=None, separators=(',', ':'))
