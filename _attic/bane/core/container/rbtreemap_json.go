package container

import (
	"encoding/json"
	"errors"
	"reflect"

	its "github.com/wrmsr/bane/core/iterators"
	ju "github.com/wrmsr/bane/core/json"
	rfl "github.com/wrmsr/bane/core/reflect"
	bt "github.com/wrmsr/bane/core/types"
)

//

func (m RbTreeMap[K, V]) MarshalJSON() ([]byte, error) {
	if m.Len() < 1 {
		return ju.EmptyObjectBytes(), nil
	}

	if ju.CanMarshalAsText(rfl.TypeOf[K]()) {
		o := make(ju.RawObject, m.Len())
		i := 0
		var err error

		m.ForEach(func(kv bt.Kv[K, V]) bool {
			var ks string
			ks, err = ju.MarshalAsText(reflect.ValueOf(kv.K))
			if err != nil {
				return false
			}

			var vb []byte
			vb, err = json.Marshal(kv.V)
			if err != nil {
				return false
			}

			o[i] = ju.RawFieldOf(ks, vb)
			i++
			return true
		})

		if err != nil {
			return nil, err
		}
		return json.Marshal(o)
	}

	s := make([][]json.RawMessage, m.Len())
	i := 0
	var err error

	m.ForEach(func(kv bt.Kv[K, V]) bool {
		var kb []byte
		kb, err = json.Marshal(kv.K)
		if err != nil {
			return false
		}

		var vb []byte
		vb, err = json.Marshal(kv.V)
		if err != nil {
			return false
		}

		s[i] = []json.RawMessage{kb, vb}
		i++
		return true
	})

	if err != nil {
		return nil, err
	}
	return json.Marshal(s)
}

func (m *RbTreeMap[K, V]) UnmarshalJSON(b []byte) error {
	m.clear()
	if len(b) < 1 {
		return errors.New("empty")
	}

	var kvs []bt.Kv[K, V]

	if b[0] == '{' {
		var o ju.RawObject
		if err := json.Unmarshal(b, &o); err != nil {
			return err
		}

		kvs = make([]bt.Kv[K, V], len(o))
		for i, f := range o {
			var k K
			if err := ju.UnmarshalAsText(f.K, reflect.ValueOf(&k).Elem()); err != nil {
				return err
			}

			var v V
			if err := json.Unmarshal(f.V, &v); err != nil {
				return err
			}

			kvs[i] = bt.KvOf(k, v)
		}

	} else {
		var s [][]json.RawMessage
		if err := json.Unmarshal(b, &s); err != nil {
			return err
		}

		kvs = make([]bt.Kv[K, V], len(s))
		for i, c := range s {
			if len(c) != 2 {
				return errors.New("expected pairs")
			}

			var k K
			if err := json.Unmarshal(c[0], &k); err != nil {
				return err
			}

			var v V
			if err := json.Unmarshal(c[1], &v); err != nil {
				return err
			}

			kvs[i] = bt.KvOf(k, v)
		}

	}

	*m = NewRbTreeMap[K, V](m.less, its.OfSlice(kvs))
	return nil
}

//

func (m MutRbTreeMap[K, V]) MarshalJSON() ([]byte, error) {
	return json.Marshal(m.m)
}

func (m *MutRbTreeMap[K, V]) UnmarshalJSON(b []byte) error {
	return json.Unmarshal(b, &m.m)
}
