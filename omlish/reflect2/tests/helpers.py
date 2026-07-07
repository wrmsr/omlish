from ..mirror import ForwardRefResolver
from ..mirror import Mirror
from ..mirror import UnresolvedForwardRefPolicy
from ..mirrorimpl import MirrorImpl


def make_mirror(
        *,
        forward_ref_resolver: ForwardRefResolver | None = None,
        unresolved_forward_ref_policy: UnresolvedForwardRefPolicy | None = None,
) -> Mirror:
    return MirrorImpl(
        forward_ref_resolver=forward_ref_resolver,
        unresolved_forward_ref_policy=unresolved_forward_ref_policy,
    )
