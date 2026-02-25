import json
import typing as ta

from ..decode import ImmediateBytesReader
from ..decode import YamlDecoder


def test_decode():
    s = """\
%YAML 1.2
---
a: 1
b: c
"""

    d = YamlDecoder(ImmediateBytesReader(s.encode()))
    v = ta.cast(ta.Any, d.decode())
    print(json.dumps(v.v, indent=2))


def test_decode2():
    s = """\
# Define a reusable block with an anchor
defaults: &defaults
  timeout: 30
  retries: 3
  headers:
    User-Agent: my-client/1.0
    Accept: application/json

# Another reusable block
auth: &auth
  headers:
    Authorization: "Bearer ${TOKEN}"

services:
  user_service:
    # Merge defaults into this mapping
    <<: *defaults
    url: https://api.example.com/users

  order_service:
    # Merge defaults, then override one field
    <<: *defaults
    url: https://api.example.com/orders
    timeout: 60

  billing_service:
    # Start from defaults...
    <<: *defaults
    # ...and also reuse the auth block
    headers:
      <<: [*defaults, *auth]   # merge multiple maps
      X-Trace-Id: "abc123"
    url: https://api.example.com/billing
"""

    d = YamlDecoder(ImmediateBytesReader(s.encode()))
    v = ta.cast(ta.Any, d.decode())
    print(json.dumps(v.v, indent=2))


def test_decode3():
    s = """\
a: &a
  self: *a
"""

    d = YamlDecoder(ImmediateBytesReader(s.encode()))
    v = ta.cast(ta.Any, d.decode())
    print(v)
