import json
import os.path

from ..decoding import yaml_decode


def test_decode():
    s = """\
%YAML 1.2
---
a: 1
b: c
"""

    v = yaml_decode(s)
    print(json.dumps(v, indent=2))


def test_decode2():
    s = """\
# Define a reusable block with an anchor
defaults: &defaults
  timeout: 30
  retries: 3
  headers:
    User-Agent: my-client/1.0
    Accept: application/json
  thingies:
    - barf
    - frab
    - 420

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

    v = yaml_decode(s)
    print(json.dumps(v, indent=2))


def test_decode3():
    s = """\
a: &a
  self: *a
"""

    v = yaml_decode(s)
    print(v)


def test_decode4():
    s = """\
welcome_message: "Welcome to the \\\"Example App\\\"!\\nEnjoy your stay."
"""

    from ..scanning import yaml_tokenize
    tks = yaml_tokenize(s)
    print(tks)

    v = yaml_decode(s)
    print(v)


def test_decode5():
    with open(os.path.join(os.path.dirname(__file__), 'sample.yaml')) as f:
        src = f.read()

    v = yaml_decode(src)
    print(v)
