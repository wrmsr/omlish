from ...content.content import Content
from ...content.parse.simple import parse_simple_content


##


READ_SYSTEM_PROMPT: Content = parse_simple_content("""\
    Use the `read` and `ls` tools instead of more general tools like `bash` or `python`.
""")


WRITE_SYSTEM_PROMPT: Content = parse_simple_content("""\
    Use the `write` tool for new files or complete rewrites, otherwise use the `edit` tool for existing file
    modification.
""")
