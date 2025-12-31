# Overview

Tools and parsers for various data formats. Provides abstractions over multiple backend implementations, self-contained
parsers where needed, and utilities for working with structured data in different serialization formats.

# Supported Formats

- **[json](https://github.com/wrmsr/omlish/blob/master/omlish/formats/json)** - JSON parsing and serialization:
  - Backend abstraction over stdlib `json`, `orjson`, `ujson`.
  - Self-contained streaming/incremental JSON parser.
  - Compact and pretty-print formatting options.
  - Encoding detection for JSON bytes.
- **[json5](https://github.com/wrmsr/omlish/blob/master/omlish/formats/json5)** - Self-contained
  [JSON5](https://json5.org/) parser with full spec compliance and test coverage.
- **[toml](https://github.com/wrmsr/omlish/blob/master/omlish/formats/toml)** - TOML parsing:
  - Lite version of stdlib `tomllib` parser for Python 3.8+ compatibility.
  - Wrapper around stdlib parser for 3.11+.
- **[ini](https://github.com/wrmsr/omlish/blob/master/omlish/formats/ini)** - INI file parsing utilities.
- **[edn](https://github.com/wrmsr/omlish/blob/master/omlish/formats/edn)** - EDN (Extensible Data Notation) parser.
- **yaml** - YAML parsing via optional `pyyaml` dependency.
- **cbor** - CBOR (Concise Binary Object Representation) via optional `cbor2` dependency.
- **pickle** - Enhanced pickle utilities via optional `cloudpickle` dependency.
- **xml** - XML utilities wrapping stdlib `xml.etree.ElementTree`.
- **dotenv** - `.env` file parsing.
- **logfmt** - Logfmt (key=value) parsing.
- **props** - Java properties file parsing.
- **repr** - Python repr parsing utilities.
- **codecs** - Format-specific codec abstractions.

# Key Features

- **Backend abstraction** - Abstract over multiple implementations (e.g., stdlib json vs orjson) with consistent API.
- **Self-contained parsers** - JSON5 and TOML parsers require no external dependencies.
- **Streaming support** - Incremental JSON parsing for large files.
- **Encoding detection** - Automatic encoding detection for JSON and other formats.
- **Compact/pretty printing** - Configurable output formatting for human or machine consumption.
- **Lite compatibility** - TOML parser works on Python 3.8+ without stdlib `tomllib`.

# Notable Modules

- **[json/backends](https://github.com/wrmsr/omlish/blob/master/omlish/formats/json/backends)** - JSON backend
  abstraction with stdlib, orjson, and ujson support.
- **[json/rendering](https://github.com/wrmsr/omlish/blob/master/omlish/formats/json/rendering.py)** - `JsonRenderer`
  for streaming JSON output.
- **[json/encoding](https://github.com/wrmsr/omlish/blob/master/omlish/formats/json/encoding.py)** - Encoding detection
  for JSON bytes.
- **[json5](https://github.com/wrmsr/omlish/blob/master/omlish/formats/json5)** - Full JSON5 parser implementation.
- **[toml](https://github.com/wrmsr/omlish/blob/master/omlish/formats/toml)** - TOML parser (lite-compatible).
- **[yaml](https://github.com/wrmsr/omlish/blob/master/omlish/formats/yaml.py)** - YAML utilities.
- **[cbor](https://github.com/wrmsr/omlish/blob/master/omlish/formats/cbor.py)** - CBOR utilities.
- **[cloudpickle](https://github.com/wrmsr/omlish/blob/master/omlish/formats/cloudpickle.py)** - Enhanced pickle
  utilities.
- **[xml](https://github.com/wrmsr/omlish/blob/master/omlish/formats/xml.py)** - XML utilities.
- **[dotenv](https://github.com/wrmsr/omlish/blob/master/omlish/formats/dotenv.py)** - `.env` file parsing.
- **[logfmt](https://github.com/wrmsr/omlish/blob/master/omlish/formats/logfmt.py)** - Logfmt parsing.
- **[props](https://github.com/wrmsr/omlish/blob/master/omlish/formats/props.py)** - Java properties parsing.
- **[repr](https://github.com/wrmsr/omlish/blob/master/omlish/formats/repr.py)** - Python repr utilities.

# Example Usage

```python
from omlish.formats import json

# Use default backend (stdlib json or orjson if available)
data = json.loads('{"key": "value"}')
text = json.dumps(data)

# Pretty printing
json.dump_pretty({'a': 1, 'b': 2}, file)

# Compact output
json.dump_compact({'a': 1, 'b': 2}, file)

# JSON5 parsing
from omlish.formats import json5
data = json5.loads('{key: "value", /* comment */ trailing: "comma",}')
```

# Design Philosophy

This package provides format parsers where:
1. No stdlib parser exists (JSON5, EDN).
2. Lite compatibility is needed (TOML for 3.8+).
3. Backend abstraction is valuable (JSON with orjson/ujson).
4. Additional utilities are needed beyond stdlib (streaming JSON).

For formats adequately handled by stdlib or well-established external libraries, thin wrappers or optional dependencies
are preferred over reimplementation.
