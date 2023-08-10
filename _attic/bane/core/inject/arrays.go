package inject

import (
	"fmt"
	"reflect"
	"sort"
	"strings"
)

//

type arrayProvider struct {
	ty reflect.Type
	ps []Provider

	sty reflect.Type
}

func newArrayProvider(ty reflect.Type, ps []Provider) arrayProvider {
	return arrayProvider{
		ty: ty,
		ps: ps,

		sty: reflect.SliceOf(ty),
	}
}

var _ Provider = arrayProvider{}

func (p arrayProvider) String() string {
	ps := make([]string, len(p.ps))
	for i, ep := range p.ps {
		ps[i] = ep.String()
	}
	sort.Strings(ps)

	var sb strings.Builder
	sb.WriteString("Array{")
	sb.WriteString(p.ty.String())
	sb.WriteString(", {")

	for i, es := range ps {
		if i > 0 {
			sb.WriteString(", ")
		}
		sb.WriteString(es)
	}

	sb.WriteString("}}")
	return sb.String()
}

func (p arrayProvider) providedTy(rec func(Key) reflect.Type) reflect.Type {
	return p.sty
}

func (p arrayProvider) providerFn() providerFn {
	l := len(p.ps)
	ps := make([]providerFn, l, l)
	for n, p := range p.ps {
		ps[n] = p.providerFn()
	}
	return func(i any) any {
		rv := reflect.MakeSlice(p.sty, l, l)
		n := 0
		for _, ep := range ps {
			o := ep(i)
			if _, ok := o.(emptyArrayProvider); !ok {
				rv.Index(n).Set(reflect.ValueOf(o))
				n++
			}
		}
		if n < l {
			rv = rv.Slice(0, n)
		}
		return rv.Interface()
	}
}

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
