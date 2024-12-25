import configparser

from ..codecs import make_object_lazy_loaded_codec
from ..codecs import make_str_object_codec
from .sections import IniSectionSettingsMap
from .sections import extract_ini_sections
from .sections import render_ini_sections


##


def loads(s: str) -> IniSectionSettingsMap:
    cp = configparser.ConfigParser()
    cp.read_string(s)
    return extract_ini_sections(cp)


def dumps(sm: IniSectionSettingsMap) -> str:
    return render_ini_sections(sm)


INI_CODEC = make_str_object_codec('ini', dumps, loads)

# @omlish-manifest
_INI_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'INI_CODEC', INI_CODEC)
