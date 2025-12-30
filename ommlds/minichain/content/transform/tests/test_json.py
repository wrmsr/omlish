from ...json import JsonContent
from ..json import JsonContentRenderer


def test_json():
    v = {'hi': ['there']}
    c = JsonContent(v)
    c2 = JsonContentRenderer().visit(c, None)
    print(c2)
