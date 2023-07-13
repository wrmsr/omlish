package pools

import (
	"sync"

	bt "github.com/wrmsr/bane/core/types"
)

type LinkedPoolLink struct {
	next, prev AnyLinkedPool
}

func (l LinkedPoolLink) Next() AnyLinkedPool { return l.next }
func (l LinkedPoolLink) Prev() AnyLinkedPool { return l.prev }

func (l *LinkedPoolLink) link(p AnyLinkedPool) {
	linkedPoolMtx.Lock()
	defer linkedPoolMtx.Unlock()

	l.prev = linkedPoolRoot
	l.next = linkedPoolRoot.Link().next
	l.prev.Link().next = p
	l.next.Link().prev = p
}

func (l *LinkedPoolLink) Unlink() {
	linkedPoolMtx.Lock()
	defer linkedPoolMtx.Unlock()

	l.prev.Link().next = l.next
	l.next.Link().prev = l.prev
	l.next = nil
	l.prev = nil
}

var (
	linkedPoolMtx  sync.Mutex
	linkedPoolRoot = (func() AnyLinkedPool {
		r := &LinkedPool[any]{}
		r.l.next = r
		r.l.prev = r
		return r
	})()
)

type AnyLinkedPool interface {
	Unwrap() any
	Link() *LinkedPoolLink
}

type LinkedPool[T any] struct {
	p Pool[T]

	l LinkedPoolLink

	_ bt.NoCopy
}

func NewLinkedPool[T any](p Pool[T]) *LinkedPool[T] {
	r := &LinkedPool[T]{p: p}
	r.l.link(r)
	return r
}

var _ Pool[int] = &LinkedPool[int]{}

func (p *LinkedPool[T]) Get() T  { return p.p.Get() }
func (p *LinkedPool[T]) Put(x T) { p.p.Put(x) }

var _ AnyLinkedPool = &LinkedPool[int]{}

func (p *LinkedPool[T]) Unwrap() any           { return p.p }
func (p *LinkedPool[T]) Link() *LinkedPoolLink { return &p.l }
