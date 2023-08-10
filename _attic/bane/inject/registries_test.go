package inject

import (
	"fmt"
	"testing"

	tu "github.com/wrmsr/bane/core/dev/testing"
)

func TestBinderRegistry(t *testing.T) {
	reg := NewBinderRegistry().
		Register(func() Bindings {
			return Bind(
				420,
				func(i int) string {
					return fmt.Sprintf("%d!", i)
				},
			)
		})

	inj := NewInjector(reg.Bind())
	tu.AssertEqual(t, ProvideAs[int](inj), 420)
	tu.AssertEqual(t, ProvideAs[string](inj), "420!")
}
