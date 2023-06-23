/*
The MIT License (MIT)

# Copyright (c) 2019 Travis Bischel

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the Software), to deal in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/
package rbtree

import (
	"math/rand"
	"testing"
)

type myInt int

func myIntLess(l, r any) bool {
	return l.(myInt) < r.(myInt)
}

func TestRbRandom(t *testing.T) {
	const bound = 50
	rng := rand.New(rand.NewSource(0))
	r := RbTree{Less: myIntLess}
	defer r.Clear()
	for i := 0; i < 10000; i++ {
		r.Insert(myInt(rng.Intn(bound)))
	}
	for i := 0; i < 500; i++ {
		if rng.Intn(3) == 0 {
			if found := r.Find(myInt(rng.Intn(bound))); found != nil {
				r.Delete(found)
			}
		} else {
			r.Insert(myInt(rng.Intn(bound)))
		}
	}
	for r.Len() > 0 {
		if rng.Intn(2) == 0 {
			r.Delete(r.Min())
		} else {
			r.Delete(r.Max())
		}
	}

	if r.Min() != nil {
		t.Error("expected len 0 min to be nil")
	}
	if r.Max() != nil {
		t.Error("expected len 0 max to be nil")
	}
}

func TestRbFind(t *testing.T) {
	r := RbTree{Less: myIntLess}
	defer r.Clear()
	for i := 0; i < 20; i++ {
		r.Insert(myInt(i))
	}
	for i := 20 - 1; i >= 0; i-- {
		max := r.Max()
		if max == nil || max.Item.(myInt) != myInt(i) {
			t.Fatal("could not get max")
		}
		found := r.Find(max.Item.(myInt))
		if found == nil {
			t.Fatal("could not find max")
		}
		r.Delete(found)
	}

	if r.Find(myInt(21)) != nil {
		t.Error("found unexpected 21")
	}
}

func TestRbFindWith(t *testing.T) {
	r := RbTree{Less: myIntLess}
	defer r.Clear()
	for i := 0; i < 20; i++ {
		r.Insert(myInt(i))
	}
	for i := 0; i < 20; i++ {
		n := r.FindWith(func(n *RbNode) int {
			v := int(n.Item.(myInt))
			return i - v
		})
		if n == nil || n.Item.(myInt) != myInt(i) {
			t.Fatalf("did not find %v", i)
		}
	}
	if r.FindWith(func(*RbNode) int { return -1 }) != nil {
		t.Error("found item when always left")
	}
	if r.FindWith(func(*RbNode) int { return 1 }) != nil {
		t.Error("found item when always right")
	}
}

func TestRbFindOrInsert(t *testing.T) {
	r := RbTree{Less: myIntLess}
	defer r.Clear()
	for i := 0; i < 20; i++ {
		for j := 0; j < 10; j++ {
			node := r.FindOrInsert(myInt(i))
			if got := int(node.Item.(myInt)); got != i {
				t.Errorf("got insert %d != exp %d", got, i)
			}
		}
	}
	if got := r.Len(); got != 20 {
		t.Errorf("got len %d != exp %d", got, 20)
	}
	i := 0
	for it := RbIterAt(r.Min()); it.Ok(); it.Right() {
		if got := it.Item().(myInt); got != myInt(i) {
			t.Errorf("got %d != exp %d", got, i)
		}
		i++
	}
}

func TestRbFindWithOrInsertWith(t *testing.T) {
	r := RbTree{Less: myIntLess}
	defer r.Clear()
	for i := 0; i < 20; i++ {
		for j := 0; j < 10; j++ {
			node := r.FindWithOrInsertWith(
				func(n *RbNode) int { return i - int(n.Item.(myInt)) },
				func() any { return myInt(i) },
			)
			if got := int(node.Item.(myInt)); got != i {
				t.Errorf("got insert %d, exp %d", got, i)
			}
		}
	}
	if got := r.Len(); got != 20 {
		t.Errorf("got len %d != exp %d", got, 20)
	}
	i := 0
	for it := RbIterAt(r.Min()); it.Ok(); it.Right() {
		if got := it.Item().(myInt); got != myInt(i) {
			t.Errorf("got %d != exp %d", got, i)
		}
		i++
	}
}

type intPtr int

func intPtrLess(l, r any) bool {
	return *(l.(*intPtr)) < *(r.(*intPtr))
}

func newIntPtr(v int) *intPtr {
	i := intPtr(v)
	return &i
}

func TestRbFix(t *testing.T) {
	r := RbTree{Less: intPtrLess}
	defer r.Clear()
	r.Insert(newIntPtr(1))
	r.Insert(newIntPtr(2))
	r.Insert(newIntPtr(3))
	r.Insert(newIntPtr(4))
	r.Insert(newIntPtr(9))
	r.Insert(newIntPtr(8))
	r.Insert(newIntPtr(7))
	r.Insert(newIntPtr(6))
	r.Insert(newIntPtr(5))

	max := r.Max()
	*max.Item.(*intPtr) = 0
	r.Fix(max)

	var exp intPtr
	for iter := RbIterAt(r.Min()); iter.Ok(); iter.Left() {
		if got := *iter.Item().(*intPtr); got != exp {
			t.Errorf("got %d != exp %d", got, exp)
		}
		exp++
	}
}

func TestRbIter(t *testing.T) {
	r := RbTree{Less: myIntLess}
	defer r.Clear()
	r.Insert(myInt(0))
	r.Insert(myInt(1))
	r.Insert(myInt(2))
	r.Insert(myInt(3))
	r.Insert(myInt(4))
	r.Insert(myInt(5))
	r.Insert(myInt(6))
	r.Insert(myInt(7))
	r.Insert(myInt(8))
	r.Insert(myInt(9))
	const end = 10

	iter := RbIterAt(RbInto(r.Min()))
	for exp := 0; exp < end; exp++ {
		if got := iter.Right().Item.(myInt); got != myInt(exp) {
			t.Errorf("got %d != exp %d", got, exp)
		}
	}

	iter.Reset(RbInto(r.Max()))
	for exp := end - 1; exp >= 0; exp-- {
		if got := iter.Left().Item.(myInt); got != myInt(exp) {
			t.Errorf("got %d != exp %d", got, exp)
		}
	}

	iter.Reset(r.Min())
	for exp := 0; exp < end; exp++ {
		if got := iter.Item().(myInt); got != myInt(exp) {
			t.Errorf("got %d != exp %d", got, exp)
		}
		iter.Right()
	}

	iter.Reset(r.Max())
	for exp := end - 1; exp >= 0; exp-- {
		if got := iter.Item().(myInt); got != myInt(exp) {
			t.Errorf("got %d != exp %d", got, exp)
		}
		iter.Left()
	}

	var exp int
	for iter := RbIterAt(r.Min()); iter.Ok(); iter.Right() {
		if got := iter.Item().(myInt); got != myInt(exp) {
			t.Errorf("got %d != exp %d", got, exp)
		}
		exp++
	}

	iter.Reset(RbInto(r.Max()))
	peek, left := iter.PeekLeft(), iter.Left()
	if peek.Item != left.Item {
		t.Error("destructive peek left")
	}
	if peek.Item != myInt(end-1) {
		t.Errorf("got bad peek left from max %d", peek.Item)
	}

	iter.Reset(RbInto(r.Min()))
	peek, right := iter.PeekRight(), iter.Right()
	if peek.Item != right.Item {
		t.Error("destructive peek right")
	}
	if peek.Item != myInt(0) {
		t.Errorf("got bad peek right from min %d", peek.Item)
	}
}
