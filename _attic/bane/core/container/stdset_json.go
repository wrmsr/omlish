package container

import (
	"encoding/json"
)

//

func (s StdSet[T]) MarshalJSON() ([]byte, error) {
	return json.Marshal(s.m)
}

func (s *StdSet[T]) UnmarshalJSON(b []byte) error {
	return json.Unmarshal(b, &s.m)
}

//

func (s MutStdSet[T]) MarshalJSON() ([]byte, error) {
	return json.Marshal(s.s.m)
}

func (s *MutStdSet[T]) UnmarshalJSON(b []byte) error {
	return json.Unmarshal(b, &s.s.m)
}
