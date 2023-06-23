package container

import (
	"fmt"
)

//

type KeyError[K any] struct {
	Key K
}

func (e KeyError[K]) String() string {
	return fmt.Sprintf("keyError{%v}", e.Key)
}

func (e KeyError[K]) Error() string {
	return e.String()
}

//

type IndexError struct {
	Index int
}

func (e IndexError) String() string {
	return fmt.Sprintf("indexError{%v}", e.Index)
}

func (e IndexError) Error() string {
	return e.String()
}
