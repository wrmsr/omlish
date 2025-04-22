import typing as ta


##


MARKDOWN_STYLE: ta.Sequence[tuple[str, str]] = [
    ('md.h1', 'bold underline'),
    ('md.h1.border', 'fg:ansiyellow nounderline'),
    ('md.h2', 'bold'),
    ('md.h2.border', 'fg:grey nobold'),
    ('md.h3', 'bold'),
    ('md.h4', 'bold italic'),
    ('md.h5', 'underline'),
    ('md.h6', 'italic'),
    ('md.code.inline', 'bg:#333'),
    ('md.strong', 'bold'),
    ('md.em', 'italic'),
    ('md.hr', 'fg:ansired'),
    ('md.ul.margin', 'fg:ansiyellow'),
    ('md.ol.margin', 'fg:ansicyan'),
    ('md.blockquote', 'fg:ansipurple'),
    ('md.blockquote.margin', 'fg:grey'),
    ('md.th', 'bold'),
    ('md.a', 'underline fg:ansibrightblue'),
    ('md.s', 'strike'),
    ('md.img', 'bg:cyan fg:black'),
    ('md.img.border', 'fg:cyan bg:default'),
]
