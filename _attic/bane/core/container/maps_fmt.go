package container

import (
	"fmt"
	"strings"

	iou "github.com/wrmsr/bane/core/io"
	bt "github.com/wrmsr/bane/core/types"
)

//

type MapFormatter struct {
	f fmt.State
}

func (mf MapFormatter) WriteString(s string) {
	iou.WriteStringDiscard(mf.f, s)
}

func (mf MapFormatter) WriteBegin() {
	if mf.f.Flag('#') {
		mf.WriteString("{")
	} else {
		mf.WriteString("[")
	}
}

func (mf MapFormatter) WriteEntry(i int, k, v any) {
	if i > 0 {
		if mf.f.Flag('#') {
			mf.WriteString(", ")
		} else {
			mf.WriteString(" ")
		}
	}
	if mf.f.Flag('#') {
		iou.FprintfDiscard(mf.f, "%#v:%#v", k, v)
	} else {
		iou.FprintfDiscard(mf.f, "%v:%v", k, v)
	}
}

func (mf MapFormatter) WriteEnd() {
	if mf.f.Flag('#') {
		mf.WriteString("}")
	} else {
		mf.WriteString("]")
	}
}

func MapFormat[K, V any](f fmt.State, m Map[K, V]) {
	mf := MapFormatter{f: f}
	mf.WriteBegin()
	i := 0
	m.ForEach(func(kv bt.Kv[K, V]) bool {
		mf.WriteEntry(i, kv.K, kv.V)
		i++
		return true
	})
	mf.WriteEnd()
}

//

type MapStringer struct {
	sb *strings.Builder
}

func (ms MapStringer) WriteBegin() {
	ms.sb.WriteString("[")
}

func (ms MapStringer) WriteEnd() {
	ms.sb.WriteString("]")
}

func (ms MapStringer) WriteEntry(i int, k, v any) {
	if i > 0 {
		ms.sb.WriteRune(' ')
	}
	iou.FprintfDiscard(ms.sb, "%v:%v", k, v)
}

func MapString[K, V any](sb *strings.Builder, m Map[K, V]) {
	ms := MapStringer{sb: sb}
	ms.WriteBegin()
	i := 0
	m.ForEach(func(kv bt.Kv[K, V]) bool {
		ms.WriteEntry(i, kv.K, kv.V)
		i++
		return true
	})
	ms.WriteEnd()
}
