package marshal

import (
	"reflect"
	"strings"
)

///

type UnhandledTypeError struct {
	ty reflect.Type
}

func (e UnhandledTypeError) Error() string {
	msg := "unhandled type"
	if e.ty.Kind() != reflect.Invalid {
		var sb strings.Builder
		_, _ = sb.WriteString(msg)
		_, _ = sb.WriteString(": ")
		_, _ = sb.WriteString(e.ty.String())
		msg = sb.String()
	}
	return msg
}

var _unhandledType = UnhandledTypeError{}

func unhandledType() UnhandledTypeError {
	return _unhandledType
}

func unhandledTypeOf(ty reflect.Type) UnhandledTypeError {
	if ty.Kind() == reflect.Invalid {
		return _unhandledType
	}
	return UnhandledTypeError{ty: ty}
}

func UnhandledType() UnhandledTypeError { return unhandledType() }

func UnhandledTypeOf(ty reflect.Type) UnhandledTypeError { return unhandledTypeOf(ty) }
