package marshal

import (
	"fmt"
	"testing"

	"github.com/wrmsr/bane/core/check"
	ju "github.com/wrmsr/bane/core/json"
)

type A struct {
	X int
	Y string
}

type B struct {
	A A
	Z int64
}

type C struct {
	B
	Z int32
}

var testC = C{
	B: B{
		A: A{
			X: 100,
			Y: "two hundred",
		},
		Z: 300,
	},
	Z: 420,
}

func TestMarshal(t *testing.T) {
	fmt.Printf("%+v\n", testC)

	em := NewDefaultManager(globalRegistry)

	m := check.Must1(em.Marshal(testC))
	fmt.Printf("%+v\n", m)
	fmt.Println(check.Must1(ju.MarshalString(m)))

	var tc2 C
	check.Must(em.Unmarshal(m, &tc2))
	fmt.Printf("%+v\n", tc2)
}
