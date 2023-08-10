package inject

import (
	"fmt"
	"reflect"
	"strings"

	rfl "github.com/wrmsr/bane/core/reflect"
)

//

type Key struct {
	ty  reflect.Type
	arr bool
	tag any
}

type keyGen interface {
	key() Key
}

func AsKey(o any) Key {
	if k, ok := o.(Key); ok {
		return k
	}

	if k, ok := o.(keyGen); ok {
		return k.key()
	}

	return Key{
		ty: rfl.AsType(o),
	}
}

//

func Array(o any) Key {
	k := AsKey(o)
	k.arr = true
	return k
}

func tag(k Key, tags ...any) Key {
	if len(tags) > 0 {
		if len(tags) > 1 {
			panic(genericErrorf("must provide at most one tag: %v", tags))
		}
		k.tag = tags[0]
	}
	return k
}

func Tag(o, tag any) Key {
	k := AsKey(o)
	k.tag = tag
	return k
}

//

type KeyOf[T any] struct {
	Tag any
}

func (o KeyOf[T]) key() Key {
	var z T
	return Key{
		ty:  reflect.TypeOf(z),
		tag: o.Tag,
	}
}

type ArrayOf[T any] struct {
	Tag any
}

func (o ArrayOf[T]) key() Key {
	var z T
	return Key{
		ty:  reflect.TypeOf(z),
		tag: o.Tag,
		arr: true,
	}
}

//

func (k Key) String() string {
	var sb strings.Builder
	sb.WriteString(fmt.Sprintf("Key{ty: %s", k.ty))
	if k.arr {
		sb.WriteString(", arr")
	}
	if k.tag != nil {
		sb.WriteString(fmt.Sprintf(", tag: %v", k.tag))
	}
	sb.WriteString("}")
	return sb.String()
}
