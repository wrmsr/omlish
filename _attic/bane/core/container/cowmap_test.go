package container

import (
	"fmt"
	"testing"

	tu "github.com/wrmsr/bane/core/dev/testing"
)

func TestCowMap(t *testing.T) {
	var m CowMap[int, string]
	tu.AssertEqual(t, m.Contains(420), false)
	m.Put(420, "four twenty")
	tu.AssertEqual(t, m.Get(420), "four twenty")
	fmt.Println(&m)
}
