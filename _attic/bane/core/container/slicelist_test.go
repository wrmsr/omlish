package container

import (
	"testing"

	tu "github.com/wrmsr/bane/core/dev/testing"
)

func TestSliceList(t *testing.T) {
	l := NewMutSliceListOf("zero", "one", "two", "three")
	tu.AssertEqual(t, l.Get(0), "zero")
	tu.AssertEqual(t, l.Get(1), "one")
	tu.AssertEqual(t, l.Get(2), "two")
	tu.AssertEqual(t, l.Get(3), "three")
	tu.AssertEqual(t, l.Len(), 4)

	l.Delete(2)
	tu.AssertEqual(t, l.Get(2), "three")
	tu.AssertEqual(t, l.Len(), 3)
}

func TestSliceListLazy(t *testing.T) {
	var l MutSliceList[int]
	tu.AssertEqual(t, l.Len(), 0)
	l.Append(420)
	tu.AssertEqual(t, l.Get(0), 420)
}
