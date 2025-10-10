#!/usr/bin/env python3
import random
import time
from io import StringIO
from rich.live import Live
from rich.markdown import Markdown
from rich.console import Console
from rich.text import Text


SAMPLE_MARKDOWN = """# Streaming Markdown Demo

This is a **demonstration** of streaming markdown content in real-time.

## Features

Here are some features being streamed:

- **Bold text** rendering
- *Italic text* support
- `inline code` blocks
- And much more!

### Code Example

```python
def hello_world():
    print("Hello, streaming markdown!")
    return True
```

## Lists and Formatting

1. First numbered item
2. Second numbered item
3. Third item with **emphasis**

> This is a blockquote that demonstrates
> how multiple lines work in streaming mode.

### Final Thoughts

The markdown is being rendered **chunk by chunk** as it arrives, and will remain visible in your terminal scrollback after completion.

```python
def _main() -> None:
    console = Console()

    # Randomly chunk the markdown text
    chunks = []
    text = SAMPLE_MARKDOWN
    pos = 0

    while pos < len(text):
        chunk_size = random.randint(10, 50)
        chunks.append(text[pos:pos + chunk_size])
        pos += chunk_size

    # Stream the markdown
    accumulated = ""

    with Live(Markdown(""), console=console, refresh_per_second=10) as live:
        for chunk in chunks:
            accumulated += chunk
            live.update(Markdown(accumulated))
            time.sleep(random.uniform(0.05, 0.2))
```
"""


def _main() -> None:
    """Stream markdown text to console in real-time with random chunking."""
    console = Console()

    # Randomly chunk the markdown text
    chunks = []
    text = SAMPLE_MARKDOWN
    pos = 0

    while pos < len(text):
        chunk_size = random.randint(10, 50)
        chunks.append(text[pos:pos + chunk_size])
        pos += chunk_size

    # Stream the markdown
    accumulated = ""
    lines_printed_to_scrollback = 0

    def get_rendered_lines(md_text: str) -> list[str]:
        """Render markdown and return all lines."""
        temp_console = Console(file=StringIO(), force_terminal=True, width=console.width)
        temp_console.print(Markdown(md_text))
        output = temp_console.file.getvalue()
        return output.splitlines()

    with Live(Text(""), console=console, refresh_per_second=10) as live:
        for chunk in chunks:
            accumulated += chunk
            all_lines = get_rendered_lines(accumulated)

            # Calculate how many lines fit in the live window
            available_height = console.height - 2

            # Determine which lines overflow and need to be printed to scrollback
            total_lines = len(all_lines)
            if total_lines > available_height:
                # Lines that should be in scrollback
                lines_for_scrollback = total_lines - available_height

                # Print any new lines that weren't already printed
                if lines_for_scrollback > lines_printed_to_scrollback:
                    new_lines_to_print = all_lines[lines_printed_to_scrollback:lines_for_scrollback]
                    for line in new_lines_to_print:
                        live.console.print(Text.from_ansi(line))
                    lines_printed_to_scrollback = lines_for_scrollback

                # Show only the bottom portion in the live window
                visible_lines = all_lines[-available_height:]
            else:
                visible_lines = all_lines

            # Update the live display
            live.update(Text.from_ansi("\n".join(visible_lines)))
            time.sleep(random.uniform(0.05, 0.2))


if __name__ == "__main__":
    _main()
