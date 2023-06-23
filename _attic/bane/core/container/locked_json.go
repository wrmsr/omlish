package container

import "encoding/json"

//

func (m *LockedMap[K, V]) MarshalJSON() ([]byte, error) {
	return json.Marshal(m.m)
}

func (m *LockedMap[K, V]) UnmarshalJSON(b []byte) error {
	return json.Unmarshal(b, &m.m)
}

//

func (m *LockedMutMap[K, V]) MarshalJSON() ([]byte, error) {
	return json.Marshal(m.m)
}

func (m *LockedMutMap[K, V]) UnmarshalJSON(b []byte) error {
	return json.Unmarshal(b, &m.m)
}
