package container

import (
	"fmt"
	"testing"

	tu "github.com/wrmsr/bane/core/dev/testing"
)

func TestCowList(t *testing.T) {
	var l CowList[int]
	tu.AssertEqual(t, l.Len(), 0)
	l.Append(420)
	tu.AssertEqual(t, l.Get(0), 420)
	fmt.Println(&l)
}
