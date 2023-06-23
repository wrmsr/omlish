package marshal

import (
	"fmt"
	"net/netip"
	"reflect"
	"testing"

	"github.com/wrmsr/bane/core/check"
	tu "github.com/wrmsr/bane/core/dev/testing"
)

func TestStdText(t *testing.T) {
	ip := check.Must1(netip.ParseAddr("127.0.0.1"))
	s := string(check.Must1(ip.MarshalText()))
	fmt.Println(s)

	rv := reflect.ValueOf(ip)
	mc := &MarshalContext{}
	m := check.Must1(NewStdTextMarshalerFactory().Make(mc, rv.Type()))
	mv := check.Must1(m.Marshal(mc, rv))
	fmt.Println(mv)

	uc := &UnmarshalContext{}
	u := check.Must1(NewStdTextUnmarshalerFactory(rv.Type()).Make(uc, rv.Type()))
	ip2 := check.Must1(u.Unmarshal(uc, mv)).Interface().(netip.Addr)
	fmt.Println(ip2)

	tu.AssertDeepEqual(t, ip, ip2)
}
