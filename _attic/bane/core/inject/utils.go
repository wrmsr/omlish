package inject

import (
	"reflect"
)

//

func Type[T any]() reflect.Type {
	var z T
	return reflect.TypeOf(z)
}
