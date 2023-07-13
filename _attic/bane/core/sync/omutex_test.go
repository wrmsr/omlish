package sync

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

func TestOMutex(t *testing.T) {
	l := OMutex{}
	var wg sync.WaitGroup
	wg.Add(2)
	go func() {
		k := 420
		for i := 0; i < 3; i++ {
			fmt.Printf("Lock(%v) = %v\n", k, l.Lock(k))
			time.Sleep(1 * time.Millisecond)
		}
		fmt.Printf("TryLock(%v) = %v\n", k, l.TryLock(k))
		l.Unlock(k)
		time.Sleep(2 * time.Second)
		for i := 0; i < 3; i++ {
			fmt.Printf("Unlock(%v) = %v\n", k, l.Unlock(k))
		}
		wg.Done()
	}()
	go func() {
		k := 421
		fmt.Printf("TryLock(%v) = %v\n", k, l.TryLock(k))
		time.Sleep(1 * time.Second)
		fmt.Printf("Lock(%v) = %v\n", k, l.Lock(k))
		fmt.Printf("Unlock(%v) = %v\n", k, l.Unlock(k))
		wg.Done()
	}()
	wg.Wait()
	fmt.Printf("%#v\n", l.State())
}
