from omlish import lang as _lang


# FIXME: too much in _marshal, circ dep hazard - okay as long as nothing but _marshal imports omlish.marshal
_lang.register_conditional_import('omlish.marshal', '._marshal', __package__)
