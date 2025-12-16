import io as _io

from omlish import lang as _lang


##


@_lang.cached_function
def read_app_css() -> str:
    tcss_rsrcs = [
        rsrc
        for rsrc in _lang.get_relative_resources(globals=globals()).values()
        if rsrc.name.endswith('.tcss')
    ]

    out = _io.StringIO()

    for i, rsrc in enumerate(tcss_rsrcs):
        if i:
            out.write('\n\n')

        out.write(f'/*** {rsrc.name} ***/\n')
        out.write('\n')

        out.write(rsrc.read_text().strip())
        out.write('\n')

    return out.getvalue()
