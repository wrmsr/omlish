import typing as ta

from .. import dataclasses as dc
from .providers import Provider
from .types import Injector
from .types import Key
from .types import ProviderFn


@dc.dataclass(frozen=True)
class ArrayProvider(Provider):
    ty: type
    ps: ta.Sequence[Provider]

    sty: type

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.sty

    def provider_fn(self) -> ProviderFn:
        pass


def array(cls: type, ps: ta.Iterable[Provider]) -> ArrayProvider:
    return ArrayProvider(
        cls,
        ps,
        ta.Sequence[cls],


"""
func (p arrayProvider) providerFn() providerFn {
    l = len(p.ps)
    ps = [p.provider_fn() for p in self.ps]

    def pfn(i: Injector) -> ta.Any:
        rv = []
        n = 0
        for ep in ps:
            o = ep(i)
            if _, ok := o.(emptyArrayProvider); !ok {
                rv.Index(n).Set(reflect.ValueOf(o))
                n++
            }
        }
        return rv
    
    return pfn

//

type emptyArrayProvider struct {
    ty reflect.Type
}

var _ Provider = emptyArrayProvider{}

func (p emptyArrayProvider) String() string {
    return fmt.Sprintf("Empty{%s}", p.ty)
}

func (p emptyArrayProvider) providedTy(rec func(Key) reflect.Type) reflect.Type {
    return p.ty
}

func (p emptyArrayProvider) providerFn() providerFn {
    return func(_ any) any {
        return p
    }
}

type EmptyArrayOf[T any] struct{}

func (pg EmptyArrayOf[T]) provider() Provider {
    var z T
    return emptyArrayProvider{ty: reflect.TypeOf(z)}
}

//

type BindArrayOf[T any] struct {
    Tag any
}

func (bg BindArrayOf[T]) binding() Binding {
    return As(ArrayOf[T]{bg.Tag}, EmptyArrayOf[T]{})
}

//

type BindArraySliceOf[T any] struct {
    Tag any
}

func (bg BindArraySliceOf[T]) binding() Binding {
    return As(ArrayOf[[]int]{bg.Tag}, Link{ArrayOf[int]{bg.Tag}})
}

"""
