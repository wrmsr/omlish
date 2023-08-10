package inject

import (
	"fmt"
	"reflect"

	eu "github.com/wrmsr/bane/core/errors"
)

//

func NewDeferInjector(bs Bindings) (*Injector, func() error) {
	inj := NewInjector(
		Append(
			Bind(Singleton{eu.NewDeferStack}),
			bs,
		),
	)
	ds := ProvideAs[*eu.DeferStack](inj)
	return inj, ds.Call
}

//

type Closer interface {
	Close() error
}

type closingProvider struct {
	p Provider
}

func Closing(o any) Provider {
	return closingProvider{p: asProvider(o)}
}

var _ Provider = closingProvider{}

func (p closingProvider) String() string {
	return fmt.Sprintf("Closing{%s}", p.p)
}

func (p closingProvider) providedTy(rec func(Key) reflect.Type) reflect.Type {
	return p.p.providedTy(rec)
}

var deferStackKey = AsKey(KeyOf[*eu.DeferStack]{})

func (p closingProvider) providerFn() providerFn {
	pfn := p.p.providerFn()
	return func(i any) any {
		ds := i.(*Injector).Provide(deferStackKey).(*eu.DeferStack)
		o := pfn(i)
		ds.DeferErr(o.(Closer).Close)
		return o
	}
}
