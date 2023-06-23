/*
Copyright (c) 2014, Alec Thomas
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

  - Redistributions of source code must retain the above copyright notice, this list of conditions and the following
    disclaimer.
  - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
    disclaimer in the documentation and/or other materials provided with the distribution.
  - Neither the name of SwapOff.org nor the names of its contributors may be used to endorse or promote products derived
    from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
package chd

import (
	"testing"

	tu "github.com/wrmsr/bane/core/dev/testing"
)

var chdSampleData = map[string]string{
	"one":   "1",
	"two":   "2",
	"three": "3",
	"four":  "4",
	"five":  "5",
	"six":   "6",
	"seven": "7",
}

func TestChdBuilder(t *testing.T) {
	b := NewChdBuilder()
	for k, v := range chdSampleData {
		b.Add([]byte(k), []byte(v))
	}
	c, err := b.Build()
	tu.AssertNoErr(t, err)
	tu.AssertEqual(t, 7, len(c.keys))
	for k, v := range chdSampleData {
		tu.AssertDeepEqual(t, []byte(v), c.Get([]byte(k)))
	}
	tu.AssertDeepEqual(t, len(c.Get([]byte("monkey"))), 0)
}
