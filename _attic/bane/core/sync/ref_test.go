package sync

import (
	"testing"

	tu "github.com/wrmsr/bane/core/dev/testing"
)

func TestRef(t *testing.T) {
	for _, fn := range []func() Ref[*int]{
		func() Ref[*int] { return NewRef(new(int)) },
		func() Ref[*int] { return NewSyncRef(new(int)) },
	} {
		r := fn()

		func() {
			p := r.Acquire()
			if p.Present() {
				defer r.Release()
			}

			*p.Value() = 10
		}()

		tu.AssertEqual(t, *r.Acquire().Value(), 10)
		r.Release()

		n := 0
		r.AddCallback(func(r Ref[*int], p *int) {
			n++
		})

		r.Release()
		tu.AssertEqual(t, r.Acquire().Present(), false)

		tu.AssertEqual(t, n, 1)
	}
}
