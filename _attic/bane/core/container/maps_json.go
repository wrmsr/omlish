package container

import (
	"encoding/json"
	"reflect"

	ju "github.com/wrmsr/bane/core/json"
	bt "github.com/wrmsr/bane/core/types"
)

//

func MapMarshalJson[K, V any](m Map[K, V]) ([]byte, error) {
	ro := make(ju.RawObject, m.Len())

	var err error
	i := 0
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

		ro[i] = bt.KvOf[string, json.RawMessage](ks, vb)
		i++
		return true
	})
	if err != nil {
		return nil, err
	}

	return json.Marshal(ro)
}
