package marshal

import (
	"fmt"
	"testing"

	"github.com/wrmsr/bane/core/check"
	tu "github.com/wrmsr/bane/core/dev/testing"
)

type MyInt int

func TestConvertUnmarshal(t *testing.T) {
	v := []MyInt{1}

	mv := check.Must1(Marshal(v))
	fmt.Println(mv)

	var v2 []MyInt
	check.Must(Unmarshal(mv, &v2))
	fmt.Println(v2)

	tu.AssertDeepEqual(t, v, v2)
}
