package inject

import (
	"fmt"
	"strings"
)

//

type Error interface {
	error

	isError()
}

//

type GenericError struct {
	Err error
}

func genericError(err error) GenericError {
	return GenericError{Err: err}
}

func genericErrorf(format string, a ...any) GenericError {
	return GenericError{Err: fmt.Errorf(format, a...)}
}

func (e GenericError) isError() {}

func (e GenericError) Error() string { return e.Err.Error() }
func (e GenericError) Unwrap() error { return e.Err }

//

type KeyError struct {
	Key Key

	Source any
	Name   string
}

var _ Error = KeyError{}

func (e KeyError) isError() {}

func (e KeyError) Error() string {
	return e.error("key error")
}

func (e KeyError) error(prefix string) string {
	var sb strings.Builder
	sb.WriteString(fmt.Sprintf("%s key: %+v", prefix, e.Key))
	if e.Source != nil {
		sb.WriteString(fmt.Sprintf(" from source: %s", e.Source))
	}
	if e.Name != "" {
		sb.WriteString(fmt.Sprintf(" with name: %s", e.Name))
	}
	return sb.String()
}

//

type UnboundKeyError struct {
	KeyError
}

func (e UnboundKeyError) Error() string {
	return e.error("unbound key")
}

//

type DuplicateKeyError struct {
	KeyError
}

func (e DuplicateKeyError) Error() string {
	return e.error("duplicate key")
}

//

type DuplicateBindingError struct {
	KeyError
}

func (e DuplicateBindingError) Error() string {
	return e.error("duplicate binding")
}
