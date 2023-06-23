package container

import (
	"encoding/json"
	"fmt"
	"testing"

	"github.com/wrmsr/bane/core/check"
	tu "github.com/wrmsr/bane/core/dev/testing"
	ju "github.com/wrmsr/bane/core/json"
	bt "github.com/wrmsr/bane/core/types"
)

func TestRbTreeMap(t *testing.T) {
	m := NewMutRbTreeMap[int, string](bt.CmpLessImpl(bt.OrderedCmp[int]), nil)
	m.Put(10, "ten")
	m.Put(20, "twenty")
	m.Put(30, "thirty")
	tu.AssertEqual(t, m.Contains(10), true)
	tu.AssertEqual(t, m.Get(10), "ten")
	tu.AssertEqual(t, m.Contains(11), false)

	m.Put(11, "eleven")
	tu.AssertEqual(t, m.Contains(11), true)

	m.Delete(20)
	tu.AssertEqual(t, m.Contains(20), false)
}

func TestRbTreeMapJson(t *testing.T) {
	m := NewMutRbTreeMap[int, string](bt.CmpLessImpl(bt.OrderedCmp[int]), nil)
	m.Put(10, "ten")
	m.Put(20, "twenty")
	m.Put(30, "thirty")
	m.Put(11, "eleven")

	j := check.Must1(ju.MarshalString(m))
	tu.AssertEqual(t, j, `{"10":"ten","11":"eleven","20":"twenty","30":"thirty"}`)

	//var m2 rbTreeMapImpl[int, string]
	//InitUnmarshal(&m2, bt.CmpLessImpl(bt.IntCmpImpl[int]()))

	m2 := RbTreeMap[int, string]{
		less: bt.CmpLessImpl(bt.OrderedCmp[int]),
	}

	tu.AssertNoErr(t, json.Unmarshal([]byte(j), &m2))
	fmt.Println(m2)

	tu.AssertEqual(t, m.Len(), m2.Len())

	tu.AssertNoErr(t, json.Unmarshal([]byte(j), &m))
	fmt.Println(m)

	tu.AssertEqual(t, m.Len(), m2.Len())
}
