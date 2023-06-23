package container

import (
	"testing"

	tu "github.com/wrmsr/bane/core/dev/testing"
	its "github.com/wrmsr/bane/core/iterators"
	"github.com/wrmsr/bane/core/slices"
	bt "github.com/wrmsr/bane/core/types"
)

func TestHashEqMap(t *testing.T) {
	he := bt.HashEqOf(
		func(v int) uintptr { return uintptr(v % 3) },
		func(l, r int) bool { return l == r },
	)

	m := NewHashEqMap[int, int](he, its.OfSlice(slices.KvsOf[int, int](
		0, 10,
		11, 20,
		12, 21,
		13, 22,
		14, 23,
		15, 24,
		16, 25,
		20, 30,
	)))

	m.verify()

	tu.AssertEqual(t, m.Get(12), 21)

	for _, k := range []int{12, 13, 14} {
		m.delete(k)
		m.print()
		m.verify()
	}
}
