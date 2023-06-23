package container

import (
	"fmt"
	"strconv"
	"testing"

	bt "github.com/wrmsr/bane/core/types"
)

type IntComparer struct{}

func (i IntComparer) Compare(left, right int) int {
	return left - right
}

func TestTreapMap(t *testing.T) {
	var m PersistentMap[int, string] = NewTreapMap[int, string](IntComparer{})
	fmt.Println("Len:", m.Len())

	for i := 0; i < 32; i++ {
		m = m.With(i, strconv.Itoa(i))
	}

	m = m.With(52, "hello")
	m = m.With(53, "world")
	m = m.With(52, "Hello")
	m = m.With(54, "I'm")
	m = m.With(55, "here")

	m.ForEach(func(kv bt.Kv[int, string]) bool {
		fmt.Println("[", kv.K, "] =", kv.V)
		return true
	})
	fmt.Println("Len:", m.Len())

	old := m.With(500, "five hundred")
	m = m.Without(53)

	fmt.Println(m.Get(53))
	fmt.Println(old.Get(53))
	fmt.Println(old.Get(52))
	fmt.Println(old.Get(500))

	for it := m.Iterate(); it.HasNext(); {
		v := it.Next()
		fmt.Println(v)
	}
}
