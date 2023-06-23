package marshal

import (
	"fmt"
	"reflect"
	"strconv"
	"testing"

	"github.com/wrmsr/bane/core/check"
	ctr "github.com/wrmsr/bane/core/container"
)

func TestReflectKvIterable(t *testing.T) {
	m := ctr.NewMapBuilder[string, string]().
		Put("100", "one hundred").
		Put("200", "two hundred").
		Build()

	mv := check.Must1(NewReflectKvIterableMarshaler(
		PrimitiveMarshaler{},
		PrimitiveMarshaler{},
	).Marshal(
		&MarshalContext{},
		reflect.ValueOf(m),
	))

	fmt.Println(mv)
}

func TestAnyKvIterable(t *testing.T) {
	m := ctr.NewMapBuilder[string, string]().
		Put("100", "one hundred").
		Put("200", "two hundred").
		Build()

	mv := check.Must1(NewAnyKvIterableMarshaler(
		PrimitiveMarshaler{},
		PrimitiveMarshaler{},
	).Marshal(
		&MarshalContext{},
		reflect.ValueOf(m),
	))

	fmt.Println(mv)
}

func benchmarkKvIterable(b *testing.B, impl Marshaler) {
	mb := ctr.NewMapBuilder[int64, string]()
	for i := 0; i < 100; i++ {
		mb.Put(int64(i), strconv.Itoa(i))
	}
	m := mb.Build()
	mc := &MarshalContext{}
	mrv := reflect.ValueOf(m)

	for n := 0; n < b.N; n++ {
		check.Must1(impl.Marshal(mc, mrv))
	}
}

func BenchmarkReflectKvIterable(b *testing.B) {
	benchmarkKvIterable(
		b,
		NewReflectKvIterableMarshaler(
			PrimitiveMarshaler{},
			PrimitiveMarshaler{},
		),
	)
}

func BenchmarkAnyKvIterable(b *testing.B) {
	benchmarkKvIterable(
		b,
		NewAnyKvIterableMarshaler(
			PrimitiveMarshaler{},
			PrimitiveMarshaler{},
		),
	)
}
