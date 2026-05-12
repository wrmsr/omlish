from .ir import AnyTypeRef
from .ir import ArrayTypeRef
from .ir import MapTypeRef
from .ir import NullableTypeRef
from .ir import PrimitiveTypeRef
from .ir import RefTypeRef
from .ir import TypeRef
from .ir import UnionTypeRef


##


class TypeAnnotationRenderer:
    def render(self, ref: TypeRef, *, quote_refs: bool = True) -> str:
        if isinstance(ref, PrimitiveTypeRef):
            return ref.python_type
        if isinstance(ref, RefTypeRef):
            return f"'{ref.name}'" if quote_refs else ref.name
        if isinstance(ref, ArrayTypeRef):
            return f'ta.Sequence[{self.render(ref.item, quote_refs=quote_refs)}]'
        if isinstance(ref, NullableTypeRef):
            return f'ta.Optional[{self.render(ref.inner, quote_refs=quote_refs)}]'
        if isinstance(ref, AnyTypeRef):
            return 'ta.Any'
        if isinstance(ref, MapTypeRef):
            if ref.value is not None:
                return f'ta.Mapping[str, {self.render(ref.value, quote_refs=quote_refs)}]'
            return 'ta.Mapping[str, ta.Any]'
        if isinstance(ref, UnionTypeRef):
            parts = ', '.join(self.render(m, quote_refs=quote_refs) for m in ref.members)
            return f'ta.Union[{parts}]'
        raise TypeError(ref)
