package marshal

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"math/big"
	"reflect"
	"strconv"

	iou "github.com/wrmsr/bane/core/io"
	ju "github.com/wrmsr/bane/core/json"
	bt "github.com/wrmsr/bane/core/types"
)

func JsonEncode(w io.Writer, v Value) error {
	switch v := v.(type) {

	case Null:
		return iou.WriteErr(w, ju.NullBytes())

	case Bool:
		return iou.WriteErr(w, ju.BoolBytes(v.v))

	case Int:
		if v.u {
			return iou.WriteErr(w, []byte(strconv.FormatUint(uint64(v.v), 10)))
		} else {
			return iou.WriteErr(w, []byte(strconv.FormatInt(v.v, 10)))
		}

	case Float:
		return ju.EncodeFloat64(w, v.v)

	case Number:
		return iou.WriteErr(w, []byte(v.v.String()))

	case String:
		return ju.EncodeString(w, v.v, false)

	case Bytes:
		return unhandledTypeOf(reflect.TypeOf(v))

	case Array:
		if _, err := w.Write([]byte{'['}); err != nil {
			return err
		}
		for i, e := range v.v {
			if i > 0 {
				if _, err := w.Write([]byte{','}); err != nil {
					return err
				}
			}
			if err := JsonEncode(w, e); err != nil {
				return err
			}
		}
		if _, err := w.Write([]byte{']'}); err != nil {
			return err
		}
		return nil

	case Object:
		if _, err := w.Write([]byte{'{'}); err != nil {
			return err
		}
		for i, kv := range v.v {
			if i > 0 {
				if _, err := w.Write([]byte{','}); err != nil {
					return err
				}
			}
			if ks, ok := kv.K.(String); ok {
				if err := JsonEncode(w, ks); err != nil {
					return err
				}
			} else {
				return unhandledTypeOf(reflect.TypeOf(v))
			}
			if _, err := w.Write([]byte{':'}); err != nil {
				return err
			}
			if err := JsonEncode(w, kv.V); err != nil {
				return err
			}
		}
		if _, err := w.Write([]byte{'}'}); err != nil {
			return err
		}
		return nil

	case Any:
		return unhandledTypeOf(reflect.TypeOf(v))

	}
	panic("unreachable")
}

func JsonMarshal(v Value) ([]byte, error) {
	b := bytes.NewBuffer(nil)
	if err := JsonEncode(b, v); err != nil {
		return nil, err
	}
	return b.Bytes(), nil
}

func (v Null) MarshalJSON() ([]byte, error)   { return JsonMarshal(v) }
func (v Bool) MarshalJSON() ([]byte, error)   { return JsonMarshal(v) }
func (v Int) MarshalJSON() ([]byte, error)    { return JsonMarshal(v) }
func (v Float) MarshalJSON() ([]byte, error)  { return JsonMarshal(v) }
func (v Number) MarshalJSON() ([]byte, error) { return JsonMarshal(v) }
func (v String) MarshalJSON() ([]byte, error) { return JsonMarshal(v) }
func (v Bytes) MarshalJSON() ([]byte, error)  { return JsonMarshal(v) }
func (v Array) MarshalJSON() ([]byte, error)  { return JsonMarshal(v) }
func (v Object) MarshalJSON() ([]byte, error) { return JsonMarshal(v) }
func (v Any) MarshalJSON() ([]byte, error)    { return JsonMarshal(v) }

//

func JsonUnmarshal(b []byte) (Value, error) {
	switch b[0] {

	case 'n':
		if !ju.IsNullBytes(b) {
			return nil, errors.New("expected null")
		}
		return _nullValue, nil

	case 't':
		if !ju.IsTrueBytes(b) {
			return nil, errors.New("expected true")
		}
		return _trueValue, nil
	case 'f':
		if !ju.IsFalseBytes(b) {
			return nil, errors.New("expected false")
		}
		return _falseValue, nil

	case '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9':
		var n json.Number
		if err := json.Unmarshal(b, &n); err != nil {
			return nil, err
		}
		if i, err := n.Int64(); err == nil {
			return Int{v: i}, nil
		}
		if f, err := n.Float64(); err == nil {
			return Float{v: f}, nil
		}
		var r big.Rat
		if _, ok := r.SetString(n.String()); ok {
			return Number{v: r}, nil
		}
		return nil, fmt.Errorf("invalid number: %s", n.String())

	case '"':
		var s string
		if err := json.Unmarshal(b, &s); err != nil {
			return nil, err
		}
		return String{v: s}, nil

	case '[':
		var s []json.RawMessage
		if err := json.Unmarshal(b, &s); err != nil {
			return nil, err
		}
		r := make([]Value, len(s))
		for i, e := range s {
			v, err := JsonUnmarshal(e)
			if err != nil {
				return nil, err
			}
			r[i] = v
		}
		return Array{v: r}, nil

	case '{':
		o, err := ju.DecodeRawObject(json.NewDecoder(bytes.NewReader(b)))
		if err != nil {
			return nil, err
		}
		s := make([]bt.Kv[Value, Value], len(o))
		for i, kv := range o {
			v, err := JsonUnmarshal(kv.V)
			if err != nil {
				return nil, err
			}
			s[i] = bt.KvOf[Value, Value](String{v: kv.K}, v)
		}
		return Object{v: s}, nil

	}
	return nil, errors.New("unexpected input")
}
