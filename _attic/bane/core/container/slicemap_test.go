package container

import (
	"fmt"
	"testing"

	its "github.com/wrmsr/bane/core/iterators"
	bt "github.com/wrmsr/bane/core/types"
)

func TestSliceMapIt(t *testing.T) {
	m := NewMutSliceMap[int, string](nil)
	m.Put(1, "one")
	m.Put(2, "two")
	m.Put(3, "three")
	m.Put(4, "four")

	fmt.Println(its.Seq[bt.Kv[int, string]](m))
	fmt.Println(its.Seq[bt.Kv[int, string]](m.ReverseIterate()))

	fmt.Println(its.Seq[bt.Kv[int, string]](m.IterateFrom(2)))
	fmt.Println(its.Seq[bt.Kv[int, string]](m.ReverseIterateFrom(2)))

	fmt.Println(its.Seq[bt.Kv[int, string]](m.IterateFrom(8)))
}

func TestSliceMapDecay(t *testing.T) {
	mm := NewMutSliceMap[int, string](nil)
	mm.Put(1, "one")
	fmt.Println(mm.Get(1))

	var m Map[int, string]
	m = mm
	//m = mm.Decay()
	fmt.Println(m.Get(1))

	m.(MutMap[int, string]).Put(2, "two")
	fmt.Println(m.Get(2))
}
