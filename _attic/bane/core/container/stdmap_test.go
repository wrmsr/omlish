package container

import (
	"fmt"
	"reflect"
	"testing"

	"github.com/wrmsr/bane/core/check"
	tu "github.com/wrmsr/bane/core/dev/testing"
	rfl "github.com/wrmsr/bane/core/reflect"
)

func TestStdMap(t *testing.T) {
	m := NewMutStdMap[int, string](nil)
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

func TestStdMapLazy(t *testing.T) {
	var m MutStdMap[int, string]
	tu.AssertEqual(t, m.Len(), 0)
	tu.AssertEqual(t, m.Contains(420), false)
	m.Put(420, "four twenty")
	tu.AssertEqual(t, m.Get(420), "four twenty")
}

//func TestMapReflect(t *testing.T) {
//	m := NewStdMap[int, string](nil)
//	ta := rfl.TypeArgs(reflect.TypeOf(m))
//	tu.AssertDeepEqual(t, ta, []reflect.Type{rfl.TypeOf[int](), rfl.TypeOf[string]()})
//}

func TestMapReflect2(t *testing.T) {
	ty := rfl.TypeOf[Map[int, string]]()
	ity := check.Ok1(ty.MethodByName("Iterate")).Type.Out(0)
	kvty := check.Ok1(ity.MethodByName("Next")).Type.Out(0)
	kty := check.Ok1(kvty.MethodByName("GetK")).Type.Out(0)
	vty := check.Ok1(kvty.MethodByName("GetV")).Type.Out(0)
	fmt.Println(kty, vty)
}

func TestStdMapReflectType(t *testing.T) {
	m := NewMutStdMap[reflect.Type, string](nil)
	m.Put(reflect.TypeOf(0), "int")
	m.Put(reflect.TypeOf(int32(0)), "int32")
	m.Put(reflect.TypeOf(int64(0)), "int64")

	tu.AssertEqual(t, m.Contains(reflect.TypeOf(1)), true)
	tu.AssertEqual(t, m.Get(reflect.TypeOf(1)), "int")
	tu.AssertEqual(t, m.Contains(reflect.TypeOf(int16(1))), false)

	m.Put(reflect.TypeOf(int16(0)), "int16")
	tu.AssertEqual(t, m.Contains(reflect.TypeOf(int16(1))), true)

	m.Delete(reflect.TypeOf(int64(1)))
	tu.AssertEqual(t, m.Contains(reflect.TypeOf(int64(1))), false)
}
