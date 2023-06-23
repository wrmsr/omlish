package container

import (
	"fmt"
	"testing"

	tu "github.com/wrmsr/bane/core/dev/testing"
	its "github.com/wrmsr/bane/core/iterators"
	"github.com/wrmsr/bane/core/slices"
	bt "github.com/wrmsr/bane/core/types"
)

type ListThing struct {
	i int

	al IntrusiveListNode[ListThing]
}

var (
	listThingAOps = NewIntrusiveListOps(func(p *ListThing) *IntrusiveListNode[ListThing] { return &p.al })
	//listThingBOps = NewIntrusiveListOps(func(p *ListThing) *IntrusiveListNode[ListThing] { return &p.bl })
)

func TestIntrusiveList(t *testing.T) {
	al := NewIntrusiveList[ListThing](listThingAOps)
	//bl := NewIntrusiveList[ListThing](listThingAOps)
	//_ = bl

	ts := slices.Map(func(i int) *ListThing { return &ListThing{i: i} }, bt.RangeTo(10).Slice())
	fmt.Println(ts)

	al.verify()
	al.PushFront(ts[1])
	//bl.PushFront(ts[2])

	al.verify()
	al.PushFront(ts[2])
	//bl.PushFront(ts[3])

	al.verify()
	al.PushFront(ts[3])

	//ll := list.New()
	//ll.PushFront(ts[1])
	//ll.PushFront(ts[2])
	//ll.PushFront(ts[4])

	al.verify()
	al.PushBack(ts[4])

	//al.PushFront(ts[4])
	//bl.PushFront(ts[5])

	al.verify()

	for c := al.head; c != nil; c = c.al.next {
		fmt.Println(c)
	}
}

type ilTest struct {
	s string
	i int
	l IntrusiveListNode[ilTest]
}

func TestIntrusiveList2(t *testing.T) {
	l := NewIntrusiveList[ilTest](NewIntrusiveListOps(func(p *ilTest) *IntrusiveListNode[ilTest] { return &p.l }))

	checkList := func(es ...*ilTest) {
		tu.AssertEqual(t, len(es), l.Len())
		tu.AssertEqual(t, len(es), its.Len[*ilTest](l))
		ls := its.Seq[*ilTest](l)
		for i := range es {
			tu.AssertEqual(t, es[i], ls[i])
		}
		if len(es) > 2 {
			tu.AssertEqual(t, es[2], l.Get(2))
		}
	}

	checkList()

	// Single element list
	e := l.PushFront(&ilTest{s: "a"})
	checkList(e)
	l.MoveToFront(e)
	checkList(e)
	l.MoveToBack(e)
	checkList(e)
	l.Remove(e)
	checkList()

	// Bigger list
	e2 := l.PushFront(&ilTest{i: 2})
	e1 := l.PushFront(&ilTest{i: 1})
	e3 := l.PushBack(&ilTest{i: 3})
	e4 := l.PushBack(&ilTest{s: "banana"})
	checkList(e1, e2, e3, e4)

	l.Remove(e2)
	checkList(e1, e3, e4)

	l.MoveToFront(e3) // move from middle
	checkList(e3, e1, e4)

	l.MoveToFront(e1)
	l.MoveToBack(e3) // move from middle
	checkList(e1, e4, e3)

	l.MoveToFront(e3) // move from back
	checkList(e3, e1, e4)
	l.MoveToFront(e3) // should be no-op
	checkList(e3, e1, e4)

	l.MoveToBack(e3) // move from front
	checkList(e1, e4, e3)
	l.MoveToBack(e3) // should be no-op
	checkList(e1, e4, e3)

	e2 = l.InsertBefore(&ilTest{i: 2}, e1) // insert before front
	checkList(e2, e1, e4, e3)
	l.Remove(e2)
	e2 = l.InsertBefore(&ilTest{i: 2}, e4) // insert before middle
	checkList(e1, e2, e4, e3)
	l.Remove(e2)
	e2 = l.InsertBefore(&ilTest{i: 2}, e3) // insert before back
	checkList(e1, e4, e2, e3)
	l.Remove(e2)

	e2 = l.InsertAfter(&ilTest{i: 2}, e1) // insert after front
	checkList(e1, e2, e4, e3)
	l.Remove(e2)
	e2 = l.InsertAfter(&ilTest{i: 2}, e4) // insert after middle
	checkList(e1, e4, e2, e3)
	l.Remove(e2)
	e2 = l.InsertAfter(&ilTest{i: 2}, e3) // insert after back
	checkList(e1, e4, e3, e2)
	l.Remove(e2)

	// Check standard iteration.
	sum := 0
	for e := l.Front(); e != nil; e = e.l.Next() {
		sum += e.i
	}
	if sum != 4 {
		t.Errorf("sum over l = %d, want 4", sum)
	}

	// Clear all elements by iterating
	var next *ilTest
	for e := l.Front(); e != nil; e = next {
		next = e.l.Next()
		l.Remove(e)
	}
	checkList()
}
