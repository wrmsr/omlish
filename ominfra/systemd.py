# @omlish-lite
import io
import typing as ta


def render_systemd_unit(settings_by_section: ta.Mapping[str, ta.Mapping[str, str]]) -> str:
    out = io.StringIO()

    for i, (section, settings) in enumerate(settings_by_section.items()):
        if i:
            out.write('\n')

        out.write(f'[{section}]\n')

        for k, v in settings.items():
            out.write(f'{k}={v}\n')

    return out.getvalue()
