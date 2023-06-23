package container

import (
	"encoding/json"
)

//

func (m ShapeMap[K, V]) MarshalJSON() ([]byte, error) {
	return MapMarshalJson[K, V](m)
}

//

func (m MutShapeMap[K, V]) MarshalJSON() ([]byte, error) {
	return json.Marshal(m.m)
}
