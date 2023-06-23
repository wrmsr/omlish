package marshal

import (
	"fmt"
	"reflect"
	"time"

	rfl "github.com/wrmsr/bane/core/reflect"
)

///

type TimeMarshaler struct {
	layout string
}

func NewTimeMarshaler(layout string) TimeMarshaler {
	return TimeMarshaler{layout: layout}
}

var _ Marshaler = TimeMarshaler{}

func (m TimeMarshaler) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	if !rv.Type().AssignableTo(rfl.Time()) {
		return nil, unhandledTypeOf(rv.Type())
	}

	t := rv.Interface().(time.Time)
	return String{v: t.Format(m.layout)}, nil
}

//

const DefaultTimeMarshalLayout = time.RFC3339Nano

func NewTimeMarshalerFactory(layout string) MarshalerFactory {
	return NewTypeMapMarshalerFactory(map[reflect.Type]Marshaler{rfl.TypeOf[time.Time](): NewTimeMarshaler(layout)})
}

///

type TimeUnmarshaler struct {
	layouts []string
}

func NewTimeUnmarshaler(layouts []string) TimeUnmarshaler {
	return TimeUnmarshaler{layouts: layouts}
}

var _ Unmarshaler = TimeUnmarshaler{}

func (u TimeUnmarshaler) Unmarshal(ctx *UnmarshalContext, mv Value) (reflect.Value, error) {
	switch mv := mv.(type) {

	case Null:
		return rfl.ZeroTime(), nil

	case String:
		for _, l := range u.layouts {
			if t, err := time.Parse(l, mv.v); err == nil {
				return reflect.ValueOf(t), nil
			}
		}
		return rfl.Invalid(), fmt.Errorf("cannot parse time: %s", mv.v)

	}
	return rfl.Invalid(), unhandledTypeOf(reflect.TypeOf(mv))
}

//

var defaultTimeUnmarshalLayouts = []string{
	time.RFC3339Nano,
	time.RFC3339,

	time.RFC1123,
	time.RFC1123Z,

	time.RFC850,

	time.RFC822Z,
	time.RFC822,

	time.StampNano,
	time.StampMicro,
	time.StampMilli,
	time.Stamp,
}

func DefaultTimeUnmarshalLayouts() []string {
	return defaultTimeUnmarshalLayouts
}

func NewTimeUnmarshalerFactory(layouts []string) UnmarshalerFactory {
	return NewTypeUnmarshalerFactory(NewTimeUnmarshaler(layouts), rfl.TypeOf[time.Time]())
}
