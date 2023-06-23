package container

import (
	"container/list"

	bt "github.com/wrmsr/bane/core/types"
)

type LinkedList[T any] struct {
	list.List
}

func NewLinkedList[T any](it bt.Iterable[T]) *LinkedList[T] {
	l := list.New()
	if it != nil {
		for it := it.Iterate(); it.HasNext(); {
			l.PushBack(it.Next())
		}
	}
	return &LinkedList[T]{List: *l}
}

var _ MutList[int] = &LinkedList[int]{}

func (l *LinkedList[T]) isMut() {}

func (l *LinkedList[T]) Len() int {
	return l.List.Len()
}

func (l *LinkedList[T]) GetElement(i int) *list.Element {
	if i < 0 || i >= l.Len() {
		panic(IndexError{Index: i})
	}
	n := l.List.Front()
	for ; i > 0; i-- {
		n = n.Next()
	}
	return n
}

func (l *LinkedList[T]) Get(i int) T {
	return l.GetElement(i).Value.(T)
}

type linkedListIterator[T any] struct {
	e *list.Element
}

var _ bt.Iterator[any] = &linkedListIterator[any]{}

func (i *linkedListIterator[T]) Iterate() bt.Iterator[T] {
	return i
}

func (i *linkedListIterator[T]) HasNext() bool {
	return i.e.Next() != nil
}

func (i *linkedListIterator[T]) Next() T {
	v := i.e.Value
	i.e = i.e.Next()
	return v.(T)
}

func (l *LinkedList[T]) Iterate() bt.Iterator[T] {
	return &linkedListIterator[T]{l.Front()}
}

func (l *LinkedList[T]) ForEach(fn func(v T) bool) bool {
	for n := l.Front(); n != nil; n = n.Next() {
		if !fn(n.Value.(T)) {
			return false
		}
	}
	return true
}

func (l *LinkedList[T]) Put(i int, v T) {
	at := l.GetElement(i)
	l.InsertBefore(v, at)
	l.Remove(at)
}

func (l *LinkedList[T]) Append(v T) {
	l.List.PushBack(v)
}

func (l *LinkedList[T]) Delete(i int) {
	l.List.Remove(l.GetElement(i))
}
