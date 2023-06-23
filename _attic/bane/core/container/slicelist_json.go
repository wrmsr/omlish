package container

import (
	"encoding/json"
)

//

func (l SliceList[T]) MarshalJSON() ([]byte, error) {
	return json.Marshal(l.s)
}

func (l *SliceList[T]) UnmarshalJSON(b []byte) error {
	return json.Unmarshal(b, &l.s)
}

//

func (l MutSliceList[T]) MarshalJSON() ([]byte, error) {
	return json.Marshal(l.l.s)
}

func (l *MutSliceList[T]) UnmarshalJSON(b []byte) error {
	return json.Unmarshal(b, &l.l.s)
}
