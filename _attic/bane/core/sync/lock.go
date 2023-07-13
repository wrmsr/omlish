package sync

import "sync"

//

type NopLock struct{}

var _ sync.Locker = NopLock{}

func (n NopLock) Lock()   {}
func (n NopLock) Unlock() {}

//

type DefaultLock struct {
	sync.Locker
}

var _ sync.Locker = DefaultLock{}

func (n DefaultLock) Lock() {
	if n.Locker != nil {
		n.Locker.Lock()
	}
}

func (n DefaultLock) Unlock() {
	if n.Locker != nil {
		n.Locker.Unlock()
	}
}

//

type DumbLock struct {
	mtx sync.Mutex
}

func (l *DumbLock) Lock() {
	l.mtx.Lock()
}

func (l *DumbLock) TryLock() bool {
	return l.mtx.TryLock()
}

func (l *DumbLock) Unlock() {
	l.mtx.Unlock()
}
