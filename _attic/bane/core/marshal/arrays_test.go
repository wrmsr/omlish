package marshal

import (
	"fmt"
	"reflect"
	"testing"

	"github.com/wrmsr/bane/core/check"
	tu "github.com/wrmsr/bane/core/dev/testing"
	rfl "github.com/wrmsr/bane/core/reflect"
)

func TestSlice(t *testing.T) {
	s := []int{1, 10, 100}

	mv := check.Must1(
		NewIndexMarshaler(
			PrimitiveMarshaler{},
		).Marshal(&MarshalContext{}, reflect.ValueOf(s)))
	fmt.Println(mv)

	s2 := rfl.As[[]int](check.Must1(
		NewSliceUnmarshaler(
			rfl.TypeOf[[]int](),
			NewConvertUnmarshaler(
				rfl.TypeOf[int](),
				PrimitiveUnmarshaler{}),
		).Unmarshal(&UnmarshalContext{}, mv)))
	fmt.Println(s2)

	tu.AssertDeepEqual(t, s, s2)
}

func TestArray(t *testing.T) {
	a := [...]int{1, 10, 100}

	mv := check.Must1(
		NewIndexMarshaler(
			PrimitiveMarshaler{},
		).Marshal(&MarshalContext{}, reflect.ValueOf(a)))
	fmt.Println(mv)

	a2 := rfl.As[[3]int](check.Must1(
		NewArrayUnmarshaler(
			rfl.TypeOf[[3]int](),
			NewConvertUnmarshaler(
				rfl.TypeOf[int](),
				PrimitiveUnmarshaler{}),
		).Unmarshal(&UnmarshalContext{}, mv)))
	fmt.Println(a2)

	tu.AssertDeepEqual(t, a, a2)
}
