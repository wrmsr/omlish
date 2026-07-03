from ..reflector import DynamicTypeNameSuffix
from ..reflector import ForwardRefResolver
from ..reflector import TypeReflector
from ..reflector import TypeReflectorImpl
from ..reflector import UnresolvedForwardRefPolicy


def make_reflector(
        *,
        dynamic_type_name_suffix: DynamicTypeNameSuffix | None = None,
        forward_ref_resolver: ForwardRefResolver | None = None,
        unresolved_forward_ref_policy: UnresolvedForwardRefPolicy | None = None,
) -> TypeReflector:
    return TypeReflectorImpl(
        dynamic_type_name_suffix=dynamic_type_name_suffix,
        forward_ref_resolver=forward_ref_resolver,
        unresolved_forward_ref_policy=unresolved_forward_ref_policy,
    )
