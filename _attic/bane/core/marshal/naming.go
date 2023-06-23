package marshal

import (
	stru "github.com/wrmsr/bane/core/strings"
	bt "github.com/wrmsr/bane/core/types"
)

//

type Naming interface {
	Name(s string) string
}

//

type funcNaming struct {
	fn func(string) string
}

func NamingOf(fn func(string) string) Naming {
	return funcNaming{fn: fn}
}

var _ Naming = funcNaming{}

func (n funcNaming) Name(s string) string {
	return n.fn(s)
}

//

func NopNaming() Naming   { return NamingOf(bt.Identity[string]()) }
func CamelNaming() Naming { return NamingOf(stru.ToCamel) }
func SnakeNaming() Naming { return NamingOf(stru.ToSnake) }
