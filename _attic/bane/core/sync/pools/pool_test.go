package pools

import (
	"fmt"
	"testing"

	tu "github.com/wrmsr/bane/core/dev/testing"
	rfl "github.com/wrmsr/bane/core/reflect"
)

func TestPool(t *testing.T) {
	p := NewTrackingPool[*int](
		NewSyncPool(func() *int { return new(int) }),
		func(p *int) uintptr { return rfl.AddressOf(p) },
	)

	xs := make([]*int, 10)
	for i := range xs {
		xs[i] = p.Get()
		tu.AssertEqual(t, len(p.m), i+1)
		*xs[i] = 420 + i
	}
	for i := range xs {
		p.Put(xs[i])
	}
	tu.AssertEqual(t, len(p.m), len(xs))

	for i := 0; i < len(xs)+3; i++ {
		x := p.Get()
		fmt.Printf("%d %x %d\n", i, x, *x)
	}
	tu.AssertEqual(t, len(p.m), len(xs)+3)
}
