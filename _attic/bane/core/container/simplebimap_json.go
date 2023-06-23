package container

import "encoding/json"

//

func (m SimpleBiMap[K, V]) MarshalJSON() ([]byte, error) {
	return json.Marshal(m.Map)
}

func (m *SimpleBiMap[K, V]) UnmarshalJSON(b []byte) error {
	return json.Unmarshal(b, &m.Map)
}

//

func (m MutSimpleBiMap[K, V]) MarshalJSON() ([]byte, error) {
	return json.Marshal(m.m)
}

func (m *MutSimpleBiMap[K, V]) UnmarshalJSON(b []byte) error {
	//return json.Unmarshal(b, &m.m)
	panic("nyi")
}
