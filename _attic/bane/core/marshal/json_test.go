package marshal

import (
	"fmt"
	"testing"

	"github.com/wrmsr/bane/core/check"
	tu "github.com/wrmsr/bane/core/dev/testing"
	ju "github.com/wrmsr/bane/core/json"
)

func TestJson(t *testing.T) {
	v := Array{v: []Value{
		Int{v: 420},
		Float{v: 4.2},
		String{v: "four twenty"},
	}}
	fmt.Println(v)

	j := check.Must1(ju.MarshalString(v))
	fmt.Println(j)

	v2 := check.Must1(JsonUnmarshal([]byte(j)))
	fmt.Println(v2)

	tu.AssertDeepEqual(t, v, v2)
}
