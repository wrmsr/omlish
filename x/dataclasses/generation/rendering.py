import hashlib

from .base import Plans


##


def render_plans(plans: Plans) -> str:
    # FIXME: ...
    return repr(plans)


def digest_plans(plans: Plans) -> str:
    m = hashlib.sha1()  # noqa
    m.update(render_plans(plans).encode('utf-8'))
    return m.hexdigest()
