package inject

import "sync"

var binderRegistrySealedErr = genericErrorf("should not be sealed")

type BinderRegistry struct {
	mtx sync.Mutex

	binders []Binder

	sealOnce sync.Once
	sealed   bool
}

func NewBinderRegistry() *BinderRegistry {
	return &BinderRegistry{}
}

var _ Bindings = &BinderRegistry{}

func (r *BinderRegistry) isBindings() {}

func (r *BinderRegistry) Register(bs ...Binder) *BinderRegistry {
	r.mtx.Lock()
	defer r.mtx.Unlock()

	if r.sealed {
		panic(binderRegistrySealedErr)
	}

	for _, b := range bs {
		if b != nil {
			r.binders = append(r.binders, b)
		}
	}

	return r
}

func (r *BinderRegistry) Seal() *BinderRegistry {
	r.sealOnce.Do(func() {
		r.mtx.Lock()
		defer r.mtx.Unlock()

		if r.sealed {
			panic(binderRegistrySealedErr)
		}

		r.sealed = true
	})
	return r
}

func (r *BinderRegistry) ForEach(fn func(v Binding) bool) bool {
	r.Seal()

	for _, b := range r.binders {
		if !b().ForEach(fn) {
			return false
		}
	}
	return true
}

func (r *BinderRegistry) Bind() Bindings {
	r.Seal()

	bs := make([]Bindings, len(r.binders))
	for i, b := range r.binders {
		bs[i] = b()
	}

	return Append(bs...)
}
