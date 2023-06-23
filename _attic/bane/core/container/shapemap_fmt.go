package container

import (
	"fmt"
	"strings"

	iou "github.com/wrmsr/bane/core/io"
)

//

func (m ShapeMap[K, V]) format(tn string, f fmt.State, c rune) {
	iou.WriteStringDiscard(f, tn)
	MapFormat[K, V](f, m)
}

func (m ShapeMap[K, V]) Format(f fmt.State, c rune) {
	m.format("shapeMap", f, c)
}

func (m ShapeMap[K, V]) string(tn string) string {
	var sb strings.Builder
	sb.WriteString(tn)
	MapString[K, V](&sb, m)
	return sb.String()
}

func (m ShapeMap[K, V]) String() string {
	return m.string("shapeMap")
}

//

func (m MutShapeMap[K, V]) String() string {
	return m.m.string("mutShapeMap")
}

func (m MutShapeMap[K, V]) Format(f fmt.State, c rune) {
	m.m.format("mutShapeMap", f, c)
}
