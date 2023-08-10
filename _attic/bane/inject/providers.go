package inject

import (
	"fmt"
	"reflect"
	"sync"
	"sync/atomic"

	rfl "github.com/wrmsr/bane/core/reflect"
	rtu "github.com/wrmsr/bane/core/runtime"
	bt "github.com/wrmsr/bane/core/types"
)

//

type Provider interface {
	String() string

	providedTy(rec func(Key) reflect.Type) reflect.Type
	providerFn() providerFn
}

type providerGen interface {
	provider() Provider
}

//

type providerMap map[Key]Provider

type providerFn = func(injector any) any
type providerFnMap map[Key]providerFn

func (pm providerMap) fns() providerFnMap {
	pfm := make(providerFnMap, len(pm))
	for k, p := range pm {
		pfm[k] = p.providerFn()
	}
	return pfm
}

//

func asProvider(o any) Provider {
	if bt.Is[Binding](o) || bt.Is[bindingGen](o) {
		panic(genericErrorf("must not use bindings as providers"))
	}

	if _, ok := o.(Bindings); ok {
		panic(genericErrorf("must not use bindings as providers"))
	}

	if o == nil {
		return constProvider{}
	}

	if o, ok := o.(Provider); ok {
		return o
	}

	if o, ok := o.(providerGen); ok {
		return o.provider()
	}

	if o, ok := o.(Key); ok {
		return Link{o}.provider()
	}

	rv := reflect.ValueOf(o)
	rt := rv.Type()
	if rt.Kind() == reflect.Func {
		return Func{o}.provider()
	}

	return constProvider{o}
}

//

type constProvider struct {
	v any
}

var _ Provider = constProvider{}

func (p constProvider) String() string {
	return fmt.Sprintf("Const{%v}", p.v)
}

func (p constProvider) providedTy(rec func(Key) reflect.Type) reflect.Type {
	return reflect.TypeOf(p.v)
}

func (p constProvider) providerFn() providerFn {
	return func(_ any) any {
		return p.v
	}
}

type Const struct {
	Val any
}

func (pg Const) provider() Provider {
	return constProvider{pg.Val}
}

//

type funcProvider struct {
	fn reflect.Value

	fty reflect.Type
	ty  reflect.Type
}

var _ Provider = funcProvider{}

func (p funcProvider) String() string {
	return fmt.Sprintf("Func{%v, %s}", rtu.GetFuncName(p.fn), p.ty)
}

func (p funcProvider) providedTy(rec func(Key) reflect.Type) reflect.Type {
	return p.ty
}

func (p funcProvider) providerFn() providerFn {
	return func(i any) any {
		return i.(*Injector).InjectOne(p.fn)
	}
}

type Func struct {
	Fn any
}

func (pg Func) provider() Provider {
	rv := rfl.AsValue(pg.Fn)
	fty := rv.Type()
	if fty.Kind() != reflect.Func {
		panic(genericErrorf("must be func: %v", rv))
	}
	if fty.NumOut() != 1 {
		panic(genericErrorf("func must have one output: %v", fty))
	}
	return funcProvider{fn: rv, fty: fty, ty: fty.Out(0)}
}

//

type linkProvider struct {
	k Key
}

var _ Provider = linkProvider{}

func (p linkProvider) String() string {
	return fmt.Sprintf("Link{%s}", p.k)
}

func (p linkProvider) providedTy(rec func(Key) reflect.Type) reflect.Type {
	return rec(p.k)
}

func (p linkProvider) providerFn() providerFn {
	return func(i any) any {
		return i.(*Injector).Provide(p.k)
	}
}

type Link struct {
	To any
}

func (pg Link) provider() Provider {
	return linkProvider{k: AsKey(pg.To)}
}

//

type singletonProvider struct {
	p Provider
}

var _ Provider = singletonProvider{}

func (p singletonProvider) String() string {
	return fmt.Sprintf("Singleton{%s}", p.p)
}

func (p singletonProvider) providedTy(rec func(Key) reflect.Type) reflect.Type {
	return p.p.providedTy(rec)
}

func (p singletonProvider) providerFn() providerFn {
	var o sync.Once
	var v atomic.Value
	type box struct{ v any }
	fn := p.p.providerFn()
	return func(i any) any {
		o.Do(func() {
			v.Store(box{fn(i)})
		})
		return v.Load().(box).v
	}
}

type Singleton struct {
	Obj any
}

func (pg Singleton) provider() Provider {
	return singletonProvider{p: asProvider(pg.Obj)}
}
