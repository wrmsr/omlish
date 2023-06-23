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
// Package mph is a Go implementation of the compress, hash and displace (CHD) minimal perfect hash algorithm.
//
// See http://cmph.sourceforge.net/papers/esa09.pdf for details.
//
// To create and serialize a hash table:
//
//		b := mph.Builder()
// 		for k, v := range data {
// 			b.Add(k, v)
// 		}
// 		h, _ := b.Build()
// 		w, _ := os.Create("data.idx")
// 		b, _ := h.Write(w)
//
// To read from the hash table:
//
//		r, _ := os.Open("data.idx")
//		h, _ := h.Read(r)
//
//		v := h.Get([]byte("some key"))
//		if v == nil {
//		    // Key not found
//		}
//
// MMAP is also indirectly supported, by deserializing from a byte slice and slicing the keys and values.
//
// See https://github.com/alecthomas/mph for source.
package chd

import (
	"bytes"
	"encoding/binary"
	"io"
)

// CHD hash table lookup.
type Chd struct {
	// Random hash function table.
	r []uint64
	// Array of indices into hash function table r. We assume there aren't more than 2^16 hash functions O_o
	indices []uint16
	// Final table of values.
	keys   [][]byte
	values [][]byte
}

func chdHash(data []byte) uint64 {
	var hash uint64 = 14695981039346656037
	for _, c := range data {
		hash ^= uint64(c)
		hash *= 1099511628211
	}
	return hash
}

// Get an entry from the hash table.
func (c *Chd) Get(key []byte) []byte {
	r0 := c.r[0]
	h := chdHash(key) ^ r0
	i := h % uint64(len(c.indices))
	ri := c.indices[i]
	// This can occur if there were unassigned slots in the hash table.
	if ri >= uint16(len(c.r)) {
		return nil
	}
	r := c.r[ri]
	ti := (h ^ r) % uint64(len(c.keys))
	// fmt.Printf("r[0]=%d, h=%d, i=%d, ri=%d, r=%d, ti=%d\n", c.r[0], h, i, ri, r, ti)
	k := c.keys[ti]
	if bytes.Compare(k, key) != 0 {
		return nil
	}
	v := c.values[ti]
	return v
}

func (c *Chd) Len() int {
	return len(c.keys)
}

// Iterate over entries in the hash table.
func (c *Chd) Iterate() *ChdIterator {
	if len(c.keys) == 0 {
		return nil
	}
	return &ChdIterator{c: c}
}

// Serialize the CHD. The serialized form is conducive to mmapped access. See the Mmap function for details.
func (c *Chd) Write(w io.Writer) error {
	write := func(nd ...any) error {
		for _, d := range nd {
			if err := binary.Write(w, binary.LittleEndian, d); err != nil {
				return err
			}
		}
		return nil
	}

	data := []any{
		uint32(len(c.r)), c.r,
		uint32(len(c.indices)), c.indices,
		uint32(len(c.keys)),
	}

	if err := write(data...); err != nil {
		return err
	}

	for i := range c.keys {
		k, v := c.keys[i], c.values[i]
		if err := write(uint32(len(k)), uint32(len(v))); err != nil {
			return err
		}
		if _, err := w.Write(k); err != nil {
			return err
		}
		if _, err := w.Write(v); err != nil {
			return err
		}
	}
	return nil
}

type ChdIterator struct {
	i int
	c *Chd
}

func (c *ChdIterator) Get() (key []byte, value []byte) {
	return c.c.keys[c.i], c.c.values[c.i]
}

func (c *ChdIterator) Next() *ChdIterator {
	c.i++
	if c.i >= len(c.c.keys) {
		return nil
	}
	return c
}
