from omlish import lang
from omlish import marshal as msh

from .types import Blob
from .types import Part
from .types import Value


##


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.install_standard_factories(
        *msh.standard_polymorphism_factories(
            msh.polymorphism_from_subclasses(Value),
        ),
    )

    msh.update_fields_metadata(
        ['data'],
        marshaler=msh.Base64MarshalerUnmarshaler(bytes),
        unmarshaler_factory=msh.Base64MarshalerUnmarshaler(bytes),
    )(Blob)

    msh.update_fields_metadata(
        ['thought_signature'],
        marshaler=msh.OptionalMarshaler(msh.Base64MarshalerUnmarshaler(bytes)),
        unmarshaler_factory=msh.OptionalUnmarshaler(msh.Base64MarshalerUnmarshaler(bytes)),
    )(Part)
