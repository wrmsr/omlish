import importlib.resources
import logging
import typing as ta

import jinja2

from omlish import lang


log = logging.getLogger(__name__)


class _J2Loader(jinja2.BaseLoader):

    def get_source(self, environment, template):
        raise TypeError

    def list_templates(self):
        raise TypeError

    def load(self, environment, name, globals=None):  # noqa
        return load_templates()[f'{name}.j2']


J2_ENV = jinja2.Environment(
    loader=_J2Loader(),
    autoescape=True,
)


@lang.cached_function
def load_templates() -> ta.Mapping[str, jinja2.Template]:
    ret: dict[str, jinja2.Template] = {}
    for fn in importlib.resources.files(__package__).joinpath('templates').iterdir():
        ret[fn.name] = J2_ENV.from_string(fn.read_text())
    return ret


class _EnvUser:
    is_authenticated = False


J2_DEFAULT_KWARGS = dict(
    get_flashed_messages=lambda: [],  # noqa
    current_user=_EnvUser(),
)


def j2_helper(fn):
    J2_DEFAULT_KWARGS[fn.__name__] = fn
    return fn


def render_template(name: str, **kwargs: ta.Any) -> bytes:
    return load_templates()[f'{name}.j2'].render(**{**J2_DEFAULT_KWARGS, **kwargs}).encode()
