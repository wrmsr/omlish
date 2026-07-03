from ..mirror import DynamicTypeNameSuffix
from ..mirror import ForwardRefResolver
from ..mirror import Mirror
from ..mirror import MirrorImpl
from ..mirror import UnresolvedForwardRefPolicy


def make_mirror(
        *,
        dynamic_type_name_suffix: DynamicTypeNameSuffix | None = None,
        forward_ref_resolver: ForwardRefResolver | None = None,
        unresolved_forward_ref_policy: UnresolvedForwardRefPolicy | None = None,
) -> Mirror:
    return MirrorImpl(
        dynamic_type_name_suffix=dynamic_type_name_suffix,
        forward_ref_resolver=forward_ref_resolver,
        unresolved_forward_ref_policy=unresolved_forward_ref_policy,
    )
