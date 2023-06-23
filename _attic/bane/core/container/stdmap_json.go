package container

import (
	"encoding/json"
)

//

func (m StdMap[K, V]) MarshalJSON() ([]byte, error) {
	return json.Marshal(m.m)
}

func (m *StdMap[K, V]) UnmarshalJSON(b []byte) error {
	return json.Unmarshal(b, &m.m)
}

//

func (m MutStdMap[K, V]) MarshalJSON() ([]byte, error) {
	return json.Marshal(m.m.m)
}

func (m *MutStdMap[K, V]) UnmarshalJSON(b []byte) error {
	return json.Unmarshal(b, &m.m.m)
}
