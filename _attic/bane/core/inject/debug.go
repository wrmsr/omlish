package inject

import (
	"fmt"
	"sort"
)

//

type Debug any

type Debugger interface {
	Debug() Debug
}

//

func debugBindings(bs Bindings) Debug {
	if bs == nil {
		return nil
	}
	var ds []string
	bs.ForEach(func(b Binding) bool {
		ds = append(ds, fmt.Sprintf("%s = %s", b.key, b.provider))
		return true
	})
	sort.Strings(ds)
	return ds
}

//

func init() {
	(&Injector{}).Debug()
}

func (i *Injector) Debug() Debug {
	return map[string]any{
		"bs": debugBindings(i.bs),
	}
}
