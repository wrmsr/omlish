package container

import (
	"fmt"
	"strings"

	iou "github.com/wrmsr/bane/core/io"
)

//

func (m SliceMap[K, V]) format(tn string, f fmt.State, c rune) {
	iou.WriteStringDiscard(f, tn)
	MapFormat[K, V](f, m)
}

func (m SliceMap[K, V]) Format(f fmt.State, c rune) {
	m.format("sliceMap", f, c)
}

func (m SliceMap[K, V]) string(tn string) string {
	var sb strings.Builder
	sb.WriteString(tn)
	MapString[K, V](&sb, m)
	return sb.String()
}

func (m SliceMap[K, V]) String() string {
	return m.string("sliceMap")
}

//

func (m MutSliceMap[K, V]) String() string {
	return m.m.string("mutSliceMap")
}

func (m MutSliceMap[K, V]) Format(f fmt.State, c rune) {
	m.m.format("mutSliceMap", f, c)
}
