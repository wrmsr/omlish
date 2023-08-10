package inject

import (
	"testing"

	tu "github.com/wrmsr/bane/core/dev/testing"
)

func TestArrays(t *testing.T) {
	inj := NewInjector(Bind(
		As(KeyOf[string]{}, "hi"),
		As(ArrayOf[int]{}, 420),
		As(ArrayOf[int]{}, 421),
	))

	tu.AssertDeepEqual(t, inj.Provide(KeyOf[string]{}), "hi")
	tu.AssertDeepEqual(t, inj.Provide(ArrayOf[int]{}), []int{420, 421})

	inj2 := inj.NewChild(Bind(
		As(KeyOf[[]int]{}, Link{ArrayOf[int]{}}),
	))
	tu.AssertDeepEqual(t, inj2.Provide(KeyOf[[]int]{}), []int{420, 421})
}

func TestEmptyArray(t *testing.T) {
	inj := NewInjector(Bind(
		BindArrayOf[int]{},
	))

	tu.AssertDeepEqual(t, inj.Provide(ArrayOf[int]{}), []int{})

	inj = NewInjector(Bind(
		BindArrayOf[int]{},
		As(ArrayOf[int]{}, 420),
		As(ArrayOf[int]{}, EmptyArrayOf[int]{}),
	))

	tu.AssertDeepEqual(t, inj.Provide(ArrayOf[int]{}), []int{420})
}
