package container

import (
	"testing"

	tu "github.com/wrmsr/bane/core/dev/testing"
	its "github.com/wrmsr/bane/core/iterators"
	bt "github.com/wrmsr/bane/core/types"
)

func TestLinkedMap(t *testing.T) {
	var m MutLinkedMap[int, string]

	m.Put(420, "four twenty")
	m.Put(3, "three")
	m.Put(100, "one hundred")

	tu.AssertDeepEqual(t, its.Seq[bt.Kv[int, string]](m.Iterate()), []bt.Kv[int, string]{
		{420, "four twenty"},
		{3, "three"},
		{100, "one hundred"},
	})

	m.Put(3, "three!")

	tu.AssertDeepEqual(t, its.Seq[bt.Kv[int, string]](m.Iterate()), []bt.Kv[int, string]{
		{420, "four twenty"},
		{100, "one hundred"},
		{3, "three!"},
	})

	m.Delete(3)

	tu.AssertDeepEqual(t, its.Seq[bt.Kv[int, string]](m.Iterate()), []bt.Kv[int, string]{
		{420, "four twenty"},
		{100, "one hundred"},
	})

	m.Delete(420)

	tu.AssertDeepEqual(t, its.Seq[bt.Kv[int, string]](m.Iterate()), []bt.Kv[int, string]{
		{100, "one hundred"},
	})

	m.Delete(100)

	tu.AssertEqual(t, m.Len(), 0)
}
