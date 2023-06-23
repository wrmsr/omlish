package marshal

import (
	"fmt"
	"reflect"
	"testing"

	"github.com/wrmsr/bane/core/check"
)

func TestSwitchMarshaler(t *testing.T) {
	m := NewSwitchMarshaler(
		PredicatedMarshaler(TrueMarshalPredicate, PrimitiveMarshaler{}),
	)

	mv := check.Must1(m.Marshal(&MarshalContext{}, reflect.ValueOf(420)))
	fmt.Println(mv)

	u := NewSwitchUnmarshaler(
		PredicatedUnmarshaler(TrueUnmarshalPredicate, PrimitiveUnmarshaler{}),
	)

	rv := check.Must1(u.Unmarshal(&UnmarshalContext{}, mv))
	fmt.Println(rv)
}
