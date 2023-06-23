package container

import (
	"fmt"
	"testing"

	"github.com/wrmsr/bane/core/check"
	tu "github.com/wrmsr/bane/core/dev/testing"
	its "github.com/wrmsr/bane/core/iterators"
	ju "github.com/wrmsr/bane/core/json"
	bt "github.com/wrmsr/bane/core/types"
)

func TestSimpleBiMap(t *testing.T) {
	bm := NewMutSimpleBiMap[int, int](its.Of[bt.Kv[int, int]](
		bt.KvOf(10, 100),
		bt.KvOf(20, 200),
		bt.KvOf(30, 300),
	))

	fmt.Println(check.Must1(ju.MarshalPretty(bm)))
	fmt.Println(check.Must1(ju.MarshalPretty(bm.Invert())))

	tu.AssertEqual(t, bm.Get(10), 100)
	tu.AssertEqual(t, bm.Invert().Get(100), 10)

	bm.Put(10, 101)

	tu.AssertEqual(t, bm.Get(10), 101)
	tu.AssertEqual(t, bm.Invert().Get(101), 10)

	tu.AssertEqual(t, bm.Invert().Contains(100), false)

	fmt.Println(check.Must1(ju.MarshalPretty(bm)))
	fmt.Println(check.Must1(ju.MarshalPretty(bm.Invert())))
}
