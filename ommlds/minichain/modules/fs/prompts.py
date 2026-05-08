import textwrap

from ...content.content import Content


##


READ_SYSTEM_PROMPT: Content = [
    textwrap.dedent("""\
        Use the `read` and `ls` tools instead of more general tools like `bash` or `python`.
    """),
]


WRITE_SYSTEM_PROMPT: Content = [
    textwrap.dedent("""\
        Use the `write` tool for new files or complete rewrites, otherwise use the `edit` tool for existing file
        modification.
    """),
]
