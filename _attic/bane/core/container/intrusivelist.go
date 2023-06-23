package container

import (
	"fmt"

	"github.com/wrmsr/bane/core/check"
	its "github.com/wrmsr/bane/core/iterators"
	bt "github.com/wrmsr/bane/core/types"
)

//

type IntrusiveListNode[T any] struct {
	next, prev *T
}

func (n IntrusiveListNode[T]) String() string {
	return fmt.Sprintf("{%16p %16p}", n.next, n.prev)
}

func (n IntrusiveListNode[T]) Next() *T { return n.next }
func (n IntrusiveListNode[T]) Prev() *T { return n.prev }

//

type IntrusiveListOps[T any] struct {
	getNode func(*T) *IntrusiveListNode[T]
}

func NewIntrusiveListOps[T any](getNode func(*T) *IntrusiveListNode[T]) IntrusiveListOps[T] {
	return IntrusiveListOps[T]{getNode: getNode}
}

func (o IntrusiveListOps[T]) GetNode(e *T) *IntrusiveListNode[T] {
	return o.getNode(e)
}

//

type IntrusiveList[T any] struct {
	o IntrusiveListOps[T]

	head, tail *T

	l int
}

func NewIntrusiveList[T any](ops IntrusiveListOps[T]) *IntrusiveList[T] {
	return &IntrusiveList[T]{o: ops}
}

func (l IntrusiveList[T]) verify() {
	if l.head == nil {
		check.Equal(l.tail, nil)
		check.Equal(l.l, 0)
		return
	}

	i := 0

	var prev *T
	for cur := l.head; cur != nil; prev, cur = cur, l.o.getNode(cur).next {
		cn := l.o.getNode(cur)
		fmt.Printf("%+v\n", cn)
		check.Equal(cn.prev, prev)
		i++
	}
	check.Equal(l.tail, prev)

	check.Equal(i, l.l)
	fmt.Println()
}

func (l IntrusiveList[T]) Len() int {
	return l.l
}

func (l IntrusiveList[T]) Front() *T {
	return l.head
}

func (l IntrusiveList[T]) Back() *T {
	return l.tail
}

type intrusiveListRef[T any] struct {
	e *T

	next, prev **T
}

func (l *IntrusiveList[T]) ref(e *T) intrusiveListRef[T] {
	n := l.o.getNode(e)
	return intrusiveListRef[T]{e: e, next: &n.next, prev: &n.prev}
}

func (l *IntrusiveList[T]) headRef() intrusiveListRef[T] {
	return intrusiveListRef[T]{next: &l.head}
}

func (l *IntrusiveList[T]) tailRef() intrusiveListRef[T] {
	return intrusiveListRef[T]{prev: &l.tail}
}

func (l *IntrusiveList[T]) next(r intrusiveListRef[T]) intrusiveListRef[T] {
	if *r.next == nil {
		return l.tailRef()
	}
	return l.ref(*r.next)
}

func (l *IntrusiveList[T]) prev(r intrusiveListRef[T]) intrusiveListRef[T] {
	if *r.prev == nil {
		return l.headRef()
	}
	return l.ref(*r.prev)
}

func (l *IntrusiveList[T]) insert(e, at intrusiveListRef[T]) {
	*e.prev = at.e
	*e.next = *at.next
	*l.prev(e).next = e.e
	*l.next(e).prev = e.e
	l.l++
}

func (l *IntrusiveList[T]) remove(e intrusiveListRef[T]) {
	*l.prev(e).next = *e.next
	*l.next(e).prev = *e.prev
	*e.next = nil
	*e.prev = nil
	l.l--
}

func (l *IntrusiveList[T]) move(e, at intrusiveListRef[T]) {
	if e.e == at.e {
		return
	}
	*l.prev(e).next = *e.next
	*l.next(e).prev = *e.prev

	*e.prev = at.e
	*e.next = *at.next
	*l.prev(e).next = e.e
	*l.next(e).prev = e.e
}

func (l *IntrusiveList[T]) Remove(e *T) *T {
	l.remove(l.ref(e))
	return e
}

func (l *IntrusiveList[T]) PushFront(v *T) *T {
	l.insert(l.ref(v), l.headRef())
	return v
}

func (l *IntrusiveList[T]) PushBack(v *T) *T {
	l.insert(l.ref(v), l.prev(l.tailRef()))
	return v
}

func (l *IntrusiveList[T]) InsertBefore(v, mark *T) *T {
	l.insert(l.ref(v), l.prev(l.ref(mark)))
	return v
}

func (l *IntrusiveList[T]) InsertAfter(v, mark *T) *T {
	l.insert(l.ref(v), l.ref(mark))
	return v
}

func (l *IntrusiveList[T]) MoveToFront(e *T) *T {
	if e != l.head {
		l.move(l.ref(e), l.headRef())
	}
	return e
}

func (l *IntrusiveList[T]) MoveToBack(e *T) *T {
	if e != l.tail {
		l.move(l.ref(e), l.prev(l.tailRef()))
	}
	return e
}

func (l *IntrusiveList[T]) MoveBefore(e, mark *T) *T {
	if e != mark {
		l.move(l.ref(e), l.prev(l.ref(mark)))
	}
	return e
}

func (l *IntrusiveList[T]) MoveAfter(e, mark *T) *T {
	if e != mark {
		l.move(l.ref(e), l.ref(mark))
	}
	return e
}

//

type intrusiveListIterator[T any] struct {
	o IntrusiveListOps[T]
	p *T
}

var _ bt.Iterator[*int] = &intrusiveListIterator[int]{}

func (i *intrusiveListIterator[T]) Iterate() bt.Iterator[*T] {
	return i
}

func (i *intrusiveListIterator[T]) HasNext() bool {
	return i.p != nil
}

func (i *intrusiveListIterator[T]) Next() *T {
	r := i.p
	i.p = i.o.getNode(r).next
	return r
}

func (l IntrusiveList[T]) Iterate() bt.Iterator[*T] {
	return &intrusiveListIterator[T]{o: l.o, p: l.head}
}

func (l IntrusiveList[T]) IterateFrom(e *T) bt.Iterator[*T] {
	return &intrusiveListIterator[T]{o: l.o, p: e}
}

//

type intrusiveListReverseIterator[T any] struct {
	o IntrusiveListOps[T]
	p *T
}

var _ bt.Iterator[*int] = &intrusiveListReverseIterator[int]{}

func (i *intrusiveListReverseIterator[T]) Iterate() bt.Iterator[*T] {
	return i
}

func (i *intrusiveListReverseIterator[T]) HasNext() bool {
	return i.p != nil
}

func (i *intrusiveListReverseIterator[T]) Next() *T {
	r := i.p
	i.p = i.o.getNode(r).prev
	return r
}

func (l *IntrusiveList[T]) ReverseIterate() bt.Iterator[*T] {
	return &intrusiveListReverseIterator[T]{o: l.o, p: l.tail}
}

func (l *IntrusiveList[T]) ReverseIterateFrom(e *T) bt.Iterator[*T] {
	return &intrusiveListReverseIterator[T]{o: l.o, p: e}
}

//

var _ List[*int] = IntrusiveList[int]{}

func (l IntrusiveList[T]) Get(i int) *T {
	return check.Ok1(its.Nth[*T](l, i))
}

func (l IntrusiveList[T]) ForEach(fn func(v *T) bool) bool {
	for c := l.head; c != nil; c = l.o.getNode(c).next {
		if !fn(c) {
			return false
		}
	}
	return true
}

//

var _ MutList[*int] = &IntrusiveList[int]{}

func (l *IntrusiveList[T]) isMut() {}

func (l *IntrusiveList[T]) Put(i int, v *T) {
	at := l.Get(i)
	l.InsertBefore(v, at)
	l.Remove(at)
}

func (l *IntrusiveList[T]) Append(v *T) {
	l.PushBack(v)
}

func (l *IntrusiveList[T]) Delete(i int) {
	l.Remove(l.Get(i))
}
