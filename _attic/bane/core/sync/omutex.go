package sync

import "sync"

type OMutexState struct {
	Owner   any
	Depth   int
	Waiters int
}

type OMutex struct {
	mtx sync.Mutex

	st OMutexState
	c  chan struct{}
}

func (l *OMutex) State() OMutexState {
	l.mtx.Lock()
	st := l.st
	l.mtx.Unlock()
	return st
}

func (l *OMutex) Lock(o any) int {
	l.mtx.Lock()
	if l.st.Owner == nil {
		if l.st.Depth != 0 {
			l.mtx.Unlock()
			panic("oops")
		}
		l.st.Owner = o
	} else if l.st.Owner != o && l.st.Owner != nil {
		if l.st.Depth < 1 {
			l.mtx.Unlock()
			panic("oops")
		}
		l.st.Waiters++
		if l.c == nil {
			l.c = make(chan struct{}, 1)
		}
		c := l.c
		l.mtx.Unlock()
		_ = <-c
		l.mtx.Lock()
		l.st.Waiters--
		if l.st.Owner != nil || l.st.Depth != 0 {
			l.mtx.Unlock()
			panic("oops")
		}
		l.st.Owner = o
	}
	l.st.Depth++
	d := l.st.Depth
	l.mtx.Unlock()
	return d
}

func (l *OMutex) TryLock(o any) int {
	l.mtx.Lock()
	var d int
	if l.st.Owner == o {
		l.st.Depth++
		d = l.st.Depth
	}
	l.mtx.Unlock()
	return d
}

type OMutexIncorrectOwnerError struct{}

func (l *OMutex) Unlock(o any) int {
	l.mtx.Lock()
	if l.st.Owner != o || l.st.Depth < 1 {
		l.mtx.Unlock()
		panic(OMutexIncorrectOwnerError{})
	}
	l.st.Depth--
	d := l.st.Depth
	if d < 1 {
		l.st.Owner = nil
		if l.st.Waiters > 0 {
			if l.c == nil {
				l.mtx.Unlock()
				panic("oops")
			}
			select {
			case l.c <- struct{}{}:
			default:
				l.mtx.Unlock()
				panic("oops")
			}
		}
	}
	l.mtx.Unlock()
	return d
}
