package inject

import (
	"fmt"
	"testing"

	"github.com/wrmsr/bane/core/check"
	tu "github.com/wrmsr/bane/core/dev/testing"
	ju "github.com/wrmsr/bane/core/json"
)

type fooInt int

func TestInjector(t *testing.T) {
	numFoos := 0
	inj := NewInjector(Bind(
		420,
		Singleton{func() fooInt {
			numFoos++
			return 2
		}},
		Func{func() string {
			return "hi"
		}},
		As(Tag(KeyOf[string]{}, "foo"), Link{KeyOf[string]{}}),
	))

	fmt.Println(check.Must1(ju.MarshalPretty(inj.Debug())))

	tu.AssertEqual(t, inj.Provide(Type[int]()).(int), 420)

	tu.AssertEqual(t, numFoos, 0)
	tu.AssertEqual(t, inj.Provide(Type[fooInt]()).(fooInt), 2)
	tu.AssertEqual(t, numFoos, 1)

	mul2 := func(i int, f fooInt) int {
		return i * int(f)
	}

	n := inj.InjectOne(mul2).(int)
	tu.AssertEqual(t, n, 840)

	tu.AssertEqual(t, numFoos, 1)
}
