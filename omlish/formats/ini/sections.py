# ruff: noqa: UP006 UP007
# @omlish-lite
import configparser
import io
import typing as ta


IniSectionSettingsMap = ta.Mapping[str, ta.Mapping[str, ta.Union[str, ta.Sequence[str]]]]  # ta.TypeAlias


##


def extract_ini_sections(cp: configparser.ConfigParser) -> IniSectionSettingsMap:
    config_dct: ta.Dict[str, ta.Any] = {}
    for sec in cp.sections():
        cd = config_dct
        for k in sec.split('.'):
            cd = cd.setdefault(k, {})
        cd.update(cp.items(sec))
    return config_dct


##


def render_ini_sections(
        settings_by_section: IniSectionSettingsMap,
) -> str:
    out = io.StringIO()

    for i, (section, settings) in enumerate(settings_by_section.items()):
        if i:
            out.write('\n')

        out.write(f'[{section}]\n')

        for k, v in settings.items():
            if isinstance(v, str):
                out.write(f'{k}={v}\n')
            else:
                for vv in v:
                    out.write(f'{k}={vv}\n')

    return out.getvalue()
