package pools

import "sync"

type trackingPoolNode struct {
	k uintptr
	v any
}

func (n *trackingPoolNode) get() {
}

func (n *trackingPoolNode) put() {
}

type TrackingPool[T any] struct {
	o Pool[T]
	k func(T) uintptr

	mtx sync.Mutex

	n sync.Pool
	m map[uintptr]*trackingPoolNode
}

func NewTrackingPool[T any](o Pool[T], k func(T) uintptr) *TrackingPool[T] {
	p := &TrackingPool[T]{
		o: o,
		k: k,

		m: make(map[uintptr]*trackingPoolNode),
	}

	p.n.New = func() any {
		return p.put(o.Get(), true)
	}

	return p
}

func (p *TrackingPool[T]) put(v T, isNew bool) *trackingPoolNode {
	k := p.k(v)

	p.mtx.Lock()
	defer p.mtx.Unlock()

	if e := p.m[k]; e != nil {
		if isNew {
			panic("key collision")
		}

		p.n.Put(e)
		e.put()
		return e
	}

	r := &trackingPoolNode{
		v: v,
		k: k,
	}

	p.m[k] = r
	r.put()
	return r
}

var _ Pool[int] = &TrackingPool[int]{}

func (p *TrackingPool[T]) Get() T {
	n := p.n.Get().(*trackingPoolNode)
	n.get()
	return n.v.(T)
}

func (p *TrackingPool[T]) Put(v T) {
	p.put(v, false)
}
