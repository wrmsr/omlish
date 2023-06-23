package marshal

import (
	"fmt"
	"reflect"
	"testing"

	"github.com/wrmsr/bane/core/check"
	tu "github.com/wrmsr/bane/core/dev/testing"
	rfl "github.com/wrmsr/bane/core/reflect"
	stu "github.com/wrmsr/bane/core/structs"
)

func TestStructs(t *testing.T) {
	asi := stu.NewStructInfoCache().Info((*A)(nil))
	am := NewObjectMarshaler(
		NewObjectMarshalerField("X", NewStructFieldGetter(asi.GetFlat("X")), PrimitiveMarshaler{}),
		NewObjectMarshalerField("Y", NewStructFieldGetter(asi.GetFlat("Y")), PrimitiveMarshaler{}),
	)

	csi := stu.NewStructInfoCache().Info((*C)(nil))
	cm := NewObjectMarshaler(
		NewObjectMarshalerField("A", NewStructFieldGetter(csi.GetFlat("A")), am),
		NewObjectMarshalerField("Z", NewStructFieldGetter(csi.GetFlat("Z")), PrimitiveMarshaler{}),
	)

	c := testC
	mv := check.Must1(cm.Marshal(&MarshalContext{}, reflect.ValueOf(c)))
	tu.AssertEqual(t, mv.String(), `{"A": {"X": 100, "Y": "two hundred"}, "Z": 420}`)

	au := NewObjectUnmarshaler(
		NewStructFactory(asi),
		NewObjectUnmarshalerField("X", NewStructFieldSetter(asi.GetFlat("X")), NewConvertUnmarshaler(rfl.TypeOf[int](), PrimitiveUnmarshaler{})),
		NewObjectUnmarshalerField("Y", NewStructFieldSetter(asi.GetFlat("Y")), PrimitiveUnmarshaler{}),
	)

	cu := NewObjectUnmarshaler(
		NewStructFactory(csi),
		NewObjectUnmarshalerField("A", NewStructFieldSetter(csi.GetFlat("A")), au),
		NewObjectUnmarshalerField("Z", NewStructFieldSetter(csi.GetFlat("Z")), NewConvertUnmarshaler(rfl.TypeOf[int32](), PrimitiveUnmarshaler{})),
	)

	c2 := check.Must1(cu.Unmarshal(&UnmarshalContext{}, mv)).Interface().(C)
	fmt.Println(c2)

	c3 := c
	c3.B.Z = 0
	tu.AssertEqual(t, c2, c3)
}
