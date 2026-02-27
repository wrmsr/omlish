import os.path

import pytest

from .... import check
from .. import meta
from .. import parsing
from ..grammars import Channel
from ..opto import optimize_grammar
from ..utils import filter_match_channels
from ..utils import only_match_rules


@pytest.mark.parametrize('optimize', [False, True])
def test_json(optimize):
    with open(os.path.join(os.path.dirname(__file__), 'json.abnf')) as f:
        g_src = f.read()

    g = meta.parse_grammar(g_src, root='JSON-text')

    if optimize:
        g = optimize_grammar(g)

    src = """\
{
  "title": "TOML Example",
  "owner": {
    "name": "Tom Preston-Werner",
    "dob": "1979-05-27T07:32:00-08:00"
  },
  "database": {
    "enabled": true,
    "ports": [
      8000,
      8001,
      8002
    ],
    "data": [
      [
        "delta",
        "phi"
      ],
      [
        3.14
      ]
    ],
    "temp_targets": {
      "cpu": 79.5,
      "case": 72.0
    }
  },
  "servers": {
    "alpha": {
      "ip": "10.0.0.1",
      "role": "frontend"
    },
    "beta": {
      "ip": "10.0.0.2",
      "role": "backend"
    }
  }
}\
"""

    m = check.not_none(parsing.parse(g, src))
    m = only_match_rules(m)
    m = filter_match_channels(
        m,
        g,
        keep=(Channel.STRUCTURE,),
        keep_children=True,
    )

    print()
    print(m.render(indent=2))
