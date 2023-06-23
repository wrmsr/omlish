package marshal

import (
	"fmt"
	"math/big"
	"reflect"
	"strconv"

	iou "github.com/wrmsr/bane/core/io"
	bt "github.com/wrmsr/bane/core/types"
)

//

type Value interface {
	Interface() any

	WriteString(w iou.DiscardStringWriter)
	String() string

	isValue()
}

type value struct{}

func (v value) isValue() {}

var (
	_ Value = Null{}
	_ Value = Bool{}
	_ Value = Int{}
	_ Value = Float{}
	_ Value = Number{}
	_ Value = String{}
	_ Value = Bytes{}
	_ Value = Array{}
	_ Value = Object{}
	_ Value = Any{}
)

//

type Simple interface {
	isSimple()
}

type simple struct {
	value
}

func (v simple) isSimple() {}

//

type Null struct {
	simple
}

var _nullValue = Null{}

func (v Null) Interface() any {
	return nil
}

//

type Bool struct {
	simple
	v bool
}

func (v Bool) V() bool { return v.v }

var (
	_trueValue  = Bool{v: true}
	_falseValue = Bool{v: false}
)

func (v Bool) Interface() any {
	return v.v
}

//

type Numeric interface {
	isNumeric()
}

type numeric struct {
	simple
}

func (v numeric) isNumeric() {}

//

type Int struct {
	numeric
	v int64
	u bool
}

func (v Int) V() int64 { return v.v }
func (v Int) U() bool  { return v.u }

func (v Int) Interface() any {
	if v.u {
		return uint64(v.v)
	} else {
		return v.v
	}
}

//

type Float struct {
	numeric
	v float64
}

func (v Float) V() float64 { return v.v }

func (v Float) Interface() any {
	return v.v
}

//

type Number struct {
	numeric
	v big.Rat
}

func (v Number) V() big.Rat { return v.v }

func (v Number) Interface() any {
	return v.v
}

//

type String struct {
	simple
	v string
}

func (v String) V() string { return v.v }

func (v String) Interface() any {
	return v.v
}

//

type Bytes struct {
	simple
	v []byte
}

func (v Bytes) V() []byte { return v.v }

func (v Bytes) Interface() any {
	return v.v
}

//

type Container interface {
	isContainer()
}

type container struct {
	value
}

func (v container) isContainer() {}

//

type Array struct {
	container
	v []Value
}

func (v Array) V() []Value { return v.v }

func (v Array) Interface() any {
	return v
}

//

type Object struct {
	container
	v []bt.Kv[Value, Value]
}

func (v Object) V() []bt.Kv[Value, Value] { return v.v }

func (v Object) Interface() any {
	return v.v // FIXME: ?
}

//

type Any struct {
	simple
	v any
}

func (v Any) V() any { return v.v }

func (v Any) Interface() any {
	return v.v
}

//

func (v Null) WriteString(w iou.DiscardStringWriter) {
	w.WriteString("null")
}

func (v Bool) WriteString(w iou.DiscardStringWriter) {
	if v.v {
		w.WriteString("true")
	} else {
		w.WriteString("false")
	}
}

func (v Int) WriteString(w iou.DiscardStringWriter) {
	if v.u {
		w.WriteString(strconv.FormatUint(uint64(v.v), 10))
	} else {
		w.WriteString(strconv.FormatInt(v.v, 10))
	}
}

func (v Float) WriteString(w iou.DiscardStringWriter) {
	w.WriteString(strconv.FormatFloat(v.v, 'g', -1, 64))
}

func (v Number) WriteString(w iou.DiscardStringWriter) {
	w.WriteString(v.v.String())
}

func (v String) WriteString(w iou.DiscardStringWriter) {
	w.WriteString("\"")
	w.WriteString(v.v)
	w.WriteString("\"")
}

func (v Bytes) WriteString(w iou.DiscardStringWriter) {
	w.WriteString(fmt.Sprintf("%v", v.v))
}

func (v Array) WriteString(w iou.DiscardStringWriter) {
	w.WriteString("[")
	for i, e := range v.v {
		if i > 0 {
			w.WriteString(", ")
		}
		e.WriteString(w)
	}
	w.WriteString("]")
}

func (v Object) WriteString(w iou.DiscardStringWriter) {
	w.WriteString("{")
	for i, kv := range v.v {
		if i > 0 {
			w.WriteString(", ")
		}
		kv.K.WriteString(w)
		w.WriteString(": ")
		kv.V.WriteString(w)
	}
	w.WriteString("}")
}

func (v Any) WriteString(w iou.DiscardStringWriter) {
	w.WriteString(fmt.Sprintf("%v", v.v))
}

func (v Null) String() string   { return iou.InvokeToString(v.WriteString) }
func (v Bool) String() string   { return iou.InvokeToString(v.WriteString) }
func (v Int) String() string    { return iou.InvokeToString(v.WriteString) }
func (v Float) String() string  { return iou.InvokeToString(v.WriteString) }
func (v Number) String() string { return iou.InvokeToString(v.WriteString) }
func (v String) String() string { return iou.InvokeToString(v.WriteString) }
func (v Bytes) String() string  { return iou.InvokeToString(v.WriteString) }
func (v Array) String() string  { return iou.InvokeToString(v.WriteString) }
func (v Object) String() string { return iou.InvokeToString(v.WriteString) }
func (v Any) String() string    { return iou.InvokeToString(v.WriteString) }

//

func MakeNull() Null                             { return _nullValue }
func MakeBool(v bool) Bool                       { return Bool{v: v} }
func MakeInt(v int64) Int                        { return Int{v: v} }
func MakeFloat(v float64) Float                  { return Float{v: v} }
func MakeNumber(v big.Rat) Number                { return Number{v: v} }
func MakeString(v string) String                 { return String{v: v} }
func MakeBytes(v []byte) Bytes                   { return Bytes{v: v} }
func MakeArray(v ...Value) Array                 { return Array{v: v} }
func MakeObject(v ...bt.Kv[Value, Value]) Object { return Object{v: v} }
func MakeAny(v any) Any                          { return Any{v: v} }

//

func MakeSimpleValue(o any) (Value, bool) {
	if o == nil {
		return _nullValue, true
	}

	switch v := o.(type) {

	case bool:
		return Bool{v: v}, true

	case int:
		return Int{v: int64(v)}, true
	case int8:
		return Int{v: int64(v)}, true
	case int16:
		return Int{v: int64(v)}, true
	case int32:
		return Int{v: int64(v)}, true
	case int64:
		return Int{v: v}, true

	case uint:
		return Int{v: int64(v), u: true}, true
	case uint8:
		return Int{v: int64(v), u: true}, true
	case uint16:
		return Int{v: int64(v), u: true}, true
	case uint32:
		return Int{v: int64(v), u: true}, true
	case uint64:
		return Int{v: int64(v), u: true}, true
	case uintptr:
		return Int{v: int64(v), u: true}, true

	case float32:
		return Float{v: float64(v)}, true
	case float64:
		return Float{v: v}, true

	case string:
		return String{v: v}, true

	}

	return nil, false
}

func MakeValueReflected(rv reflect.Value) (Value, bool) {
	switch rv.Kind() {
	case
		reflect.Bool,

		reflect.Int,
		reflect.Int8,
		reflect.Int16,
		reflect.Int32,
		reflect.Int64,

		reflect.Uint,
		reflect.Uint8,
		reflect.Uint16,
		reflect.Uint32,
		reflect.Uint64,
		reflect.Uintptr,

		reflect.Float32,
		reflect.Float64,

		reflect.String:
		return MakeSimpleValue(rv.Interface())

	case
		reflect.Array,
		reflect.Slice:
		if rv.Kind() == reflect.Slice && rv.IsNil() {
			return _nullValue, true
		}
		l := rv.Len()
		s := make([]Value, 0, l)
		for i := 0; i < l; i++ {
			er := rv.Index(i)
			em, ok := MakeValueReflected(er)
			if !ok {
				return nil, false
			}
			s[i] = em
		}
		return Array{v: s}, true

	case reflect.Map:
		if rv.IsNil() {
			return _nullValue, true
		}
		s := make([]bt.Kv[Value, Value], rv.Len())
		for i, mr := 0, rv.MapRange(); mr.Next(); i++ {
			kr := mr.Key()
			km, ok := MakeValueReflected(kr)
			if !ok {
				return nil, false
			}
			vr := mr.Value()
			vm, ok := MakeValueReflected(vr)
			if !ok {
				return nil, false
			}
			s[i] = bt.KvOf(km, vm)
		}

	case reflect.Pointer:
		if rv.IsNil() {
			return _nullValue, true
		}
		return MakeValueReflected(rv.Elem())

	case reflect.Interface:
		panic("nyi")

	case reflect.Struct:
		panic("nyi")

	}
	return nil, false
}

func MakeValue(v any) (Value, bool) {
	return MakeValueReflected(reflect.ValueOf(v))
}
