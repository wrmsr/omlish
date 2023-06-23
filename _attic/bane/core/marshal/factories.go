package marshal

import (
	"fmt"
	"reflect"
	"sync/atomic"

	syncu "github.com/wrmsr/bane/core/sync"
	bt "github.com/wrmsr/bane/core/types"
)

///

type Factory[R, C, A any] interface {
	Make(ctx C, a A) (R, error)
}

//

type FuncFactory[R, C, A any] struct {
	fn func(ctx C, a A) (R, error)
}

func NewFuncFactory[R, C, A any](fn func(ctx C, a A) (R, error)) FuncFactory[R, C, A] {
	return FuncFactory[R, C, A]{fn: fn}
}

var _ Factory[int, uint, string] = FuncFactory[int, uint, string]{}

func (f FuncFactory[R, C, A]) Make(ctx C, a A) (R, error) {
	return f.fn(ctx, a)
}

//

type TypeMapFactory[R, C any] struct {
	m map[reflect.Type]R
}

func NewTypeMapFactory[R, C any](m map[reflect.Type]R) TypeMapFactory[R, C] {
	return TypeMapFactory[R, C]{m: m}
}

var _ Factory[int, uint, reflect.Type] = TypeMapFactory[int, uint]{}

func (f TypeMapFactory[R, C]) Make(ctx C, a reflect.Type) (R, error) {
	if m, ok := f.m[a]; ok {
		return m, nil
	}
	var z R
	return z, nil
}

//

type TypeCacheFactory[R any, C BaseContext] struct {
	f Factory[R, C, reflect.Type]

	m atomic.Value // map[reflect.Type]bt.Optional[R]

	mtx syncu.OMutex
	nm  map[reflect.Type]bt.Optional[R]
}

func NewTypeCacheFactory[R any, C BaseContext](f Factory[R, C, reflect.Type]) *TypeCacheFactory[R, C] {
	ret := &TypeCacheFactory[R, C]{
		f: f,
	}
	ret.m.Store(make(map[reflect.Type]bt.Optional[R]))
	return ret
}

var _ Factory[int, BaseContext, reflect.Type] = &TypeCacheFactory[int, BaseContext]{}

func (f *TypeCacheFactory[R, C]) Make(ctx C, a reflect.Type) (ret R, err error) {
	m := f.m.Load().(map[reflect.Type]bt.Optional[R])
	if r, ok := m[a]; ok {
		return r.OrZero(), nil
	}

	d := f.mtx.Lock(ctx)
	defer func() {
		if d == 1 && f.nm != nil {
			if err == nil {
				f.m.Store(f.nm)
			}
			f.nm = nil
		}
		f.mtx.Unlock(ctx)
	}()

	if d == 1 {
		if f.nm != nil {
			panic("oops")
		}

		m = f.m.Load().(map[reflect.Type]bt.Optional[R])
		if r, ok := m[a]; ok {
			return r.OrZero(), nil
		}

		f.nm = make(map[reflect.Type]bt.Optional[R], len(m)+16)
		for k, v := range m {
			f.nm[k] = v
		}

	} else {
		if f.nm == nil {
			panic("oops")
		}

		if r, ok := f.nm[a]; ok {
			return r.OrZero(), nil
		}
	}

	ret, err = f.f.Make(ctx, a)
	if err != nil {
		var z R
		return z, err
	}

	if !reflect.ValueOf(ret).IsValid() {
		f.nm[a] = bt.None[R]()
	} else {
		f.nm[a] = bt.Just(ret)
	}

	return
}

//

type RecursiveTypeFactory[R, C any] struct {
	f Factory[R, C, reflect.Type]
	p func() (R, func(R))
	m map[reflect.Type]R
}

func NewRecursiveTypeFactory[R, C any](f Factory[R, C, reflect.Type], p func() (R, func(R))) RecursiveTypeFactory[R, C] {
	return RecursiveTypeFactory[R, C]{
		f: f,
		p: p,
		m: make(map[reflect.Type]R),
	}
}

var _ Factory[int, uint, reflect.Type] = RecursiveTypeFactory[int, uint]{}

func (f RecursiveTypeFactory[R, C]) Make(ctx C, a reflect.Type) (R, error) {
	if r, ok := f.m[a]; ok {
		return r, nil
	}
	p, sp := f.p()
	f.m[a] = p
	defer delete(f.m, a)
	i, err := f.f.Make(ctx, a)
	if err != nil {
		var z R
		return z, err
	}
	sp(i)
	return i, nil
}

//

type CompositeStrategy int8

const (
	FirstComposite CompositeStrategy = iota
	OneComposite
)

type CompositeFactory[R, C, A any] struct {
	st CompositeStrategy
	fs []Factory[R, C, A]
}

func NewCompositeFactory[R, C, A any](st CompositeStrategy, fs ...Factory[R, C, A]) CompositeFactory[R, C, A] {
	return CompositeFactory[R, C, A]{st: st, fs: fs}
}

var _ Factory[int, uint, string] = CompositeFactory[int, uint, string]{}

func (f CompositeFactory[R, C, A]) Make(ctx C, a A) (R, error) {
	var w []R
	for _, c := range f.fs {
		r, err := c.Make(ctx, a)
		if err != nil {
			var z R
			return z, err
		}
		if !reflect.ValueOf(r).IsValid() {
			continue
		}
		if f.st == FirstComposite {
			return r, nil
		}
		w = append(w, r)
	}

	if len(w) < 1 {
		var z R
		return z, fmt.Errorf("no implementations: %v", a)
	}

	if len(w) == 1 {
		return w[0], nil
	}

	switch f.st {

	case OneComposite:
		if len(w) == 1 {
			return w[0], nil
		}

		var z R
		return z, fmt.Errorf("multiple implementations: %v %#v", a, w)

	default:
		panic(fmt.Errorf("unknown composite strategy: %v", f.st))
	}
}
