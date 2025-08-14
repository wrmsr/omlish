from ....text.mangle import StringMangler


##


ESCAPED_IDENT_CHARS = ''.join(
    chr(i)
    for i in range(128)
    if not (
        chr(i).isalpha() or
        chr(i).isdigit() or
        chr(i) == '_' or
        ord(chr(i)) > 127
    )
)

IDENT_MANGLER = StringMangler.of('_', ESCAPED_IDENT_CHARS)
