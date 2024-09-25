from .... import marshal as msh
from ....formats import json
from ..types import request
from ..types import result


def test_marshal():
    for obj in [
        request(0, 'foo'),
        result(0, 'bar'),
    ]:
        m = msh.marshal(obj)
        j = json.dumps(m)
        print(j)
        d = json.loads(j)
        u = msh.unmarshal(d, type(obj))
        print(u)
        assert u == obj
