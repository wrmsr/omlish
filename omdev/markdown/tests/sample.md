# Streaming Markdown Demo

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

The markdown is being rendered **chunk by chunk** as it arrives.

```python
def _main() -> None:
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

    with Parser() as parser:
        for chunk in chunks:
            accumulated += chunk
            parser.update(accumulated)
            time.sleep(random.uniform(0.05, 0.2))
```
