# Overview

Text processing utilities including template rendering, text wrapping, delimiter handling, and specialized parsers.
Provides lightweight alternatives to heavy dependencies for common text operations.

# Key Components

- **[manja](https://github.com/wrmsr/omlish/blob/master/omlish/text/manja.py)** - Minimal Jinja-like template engine
  without the full Jinja2 dependency.
- **[docwrap](https://github.com/wrmsr/omlish/blob/master/omlish/text/docwrap)** - Enhanced docstring wrapping and
  formatting.
- **[antlr](https://github.com/wrmsr/omlish/blob/master/omlish/text/antlr)** - ANTLR parser integration and utilities.
- **[go](https://github.com/wrmsr/omlish/blob/master/omlish/text/go)** - Go-style text/template parsing.
- **asdl** - Abstract Syntax Description Language parsing.
- **delimit** - Delimiter-based text splitting and parsing.
- **glyphsplit** - Glyph-aware string splitting (handles multi-byte characters).
- **parts** - Text part manipulation and assembly.
- **textwrap** - Enhanced text wrapping beyond stdlib `textwrap`.
- **filecache** - File-based caching for text processing.

# Notable Modules

- **[manja](https://github.com/wrmsr/omlish/blob/master/omlish/text/manja.py)** - Lightweight Jinja-like templating:
  - Variable interpolation: `{{var}}`.
  - Conditionals: `{% if cond %}...{% endif %}`.
  - Loops: `{% for item in items %}...{% endfor %}`.
  - No heavy Jinja2 dependency.
- **[docwrap](https://github.com/wrmsr/omlish/blob/master/omlish/text/docwrap)** - Docstring formatting and wrapping
  with indentation awareness.
- **[delimit](https://github.com/wrmsr/omlish/blob/master/omlish/text/delimit.py)** - Delimiter-based parsing for
  structured text.
- **[glyphsplit](https://github.com/wrmsr/omlish/blob/master/omlish/text/glyphsplit.py)** - Unicode-aware string
  splitting.
- **[parts](https://github.com/wrmsr/omlish/blob/master/omlish/text/parts.py)** - Text part composition and
  manipulation.
- **[textwrap](https://github.com/wrmsr/omlish/blob/master/omlish/text/textwrap.py)** - Enhanced text wrapping
  utilities.
- **[asdl](https://github.com/wrmsr/omlish/blob/master/omlish/text/asdl.py)** - ASDL parsing for Python's AST
  definitions.
- **[filecache](https://github.com/wrmsr/omlish/blob/master/omlish/text/filecache.py)** - File-based text caching.

# Example Usage

```python
from omlish.text import manja

# Simple template rendering
template = manja.Template("Hello, {{name}}!")
result = template.render(name="World")  # "Hello, World!"

# Conditionals and loops
template = manja.Template("""
{% for item in items %}
  {% if item.active %}
    - {{item.name}}
  {% endif %}
{% endfor %}
""")
result = template.render(items=[
    {'name': 'Foo', 'active': True},
    {'name': 'Bar', 'active': False},
])
```

# Design Philosophy

Text utilities should:
- **Minimize dependencies** - Avoid pulling in large libraries for simple tasks (hence `manja` instead of Jinja2).
- **Be Unicode-aware** - Handle multi-byte characters correctly (`glyphsplit`).
- **Be composable** - Small utilities that can be combined for complex tasks.
- **Be self-contained** - Work without external tools or dependencies where possible.

The `manja` template engine is particularly notable as a lightweight alternative to Jinja2 for cases where full Jinja2
features aren't needed but you still want template rendering.
