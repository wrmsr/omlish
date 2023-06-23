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
	"errors"
	"fmt"
	"math/rand"
	"sort"
	"time"
)

type chdHasher struct {
	r       []uint64
	size    uint64
	buckets uint64
	rand    *rand.Rand
}

type chdBucket struct {
	index  uint64
	keys   [][]byte
	values [][]byte
}

func (b *chdBucket) String() string {
	a := "bucket{"
	for _, k := range b.keys {
		a += string(k) + ", "
	}
	return a + "}"
}

// Intermediate data structure storing buckets + outer hash index.
type chdBucketVector []chdBucket

func (b chdBucketVector) Len() int           { return len(b) }
func (b chdBucketVector) Less(i, j int) bool { return len(b[i].keys) > len(b[j].keys) }
func (b chdBucketVector) Swap(i, j int)      { b[i], b[j] = b[j], b[i] }

// Build a new CDH MPH.
type ChdBuilder struct {
	keys   [][]byte
	values [][]byte
}

// Create a new Chd hash table builder.
func NewChdBuilder() *ChdBuilder {
	return &ChdBuilder{}
}

// Add a key and value to the hash table.
func (b *ChdBuilder) Add(key []byte, value []byte) {
	b.keys = append(b.keys, key)
	b.values = append(b.values, value)
}

// Try to find a hash function that does not cause collisions with table, when applied to the keys in the bucket.
func chdTryHash(
	hasher *chdHasher,
	seen map[uint64]bool,
	keys [][]byte,
	values [][]byte,
	indices []uint16,
	bucket *chdBucket,
	ri uint16,
	r uint64,
) bool {
	// Track duplicates within this bucket.
	duplicate := make(map[uint64]bool)
	// Make hashes for each entry in the bucket.
	hashes := make([]uint64, len(bucket.keys))
	for i, k := range bucket.keys {
		h := hasher.Table(r, k)
		hashes[i] = h
		if seen[h] {
			return false
		}
		if duplicate[h] {
			return false
		}
		duplicate[h] = true
	}

	// Update seen hashes
	for _, h := range hashes {
		seen[h] = true
	}

	// Add the hash index.
	indices[bucket.index] = ri

	// Update the the hash table.
	for i, h := range hashes {
		keys[h] = bucket.keys[i]
		values[h] = bucket.values[i]
	}
	return true
}

func (b *ChdBuilder) Build() (*Chd, error) {
	n := uint64(len(b.keys))
	m := n / 2
	if m == 0 {
		m = 1
	}

	keys := make([][]byte, n)
	values := make([][]byte, n)
	hasher := newChdHasher(n, m)
	buckets := make(chdBucketVector, m)
	indices := make([]uint16, m)
	// An extra check to make sure we don't use an invalid index
	for i := range indices {
		indices[i] = ^uint16(0)
	}
	// Have we seen a hash before?
	seen := make(map[uint64]bool)
	// Used to ensure there are no duplicate keys.
	duplicates := make(map[string]bool)

	for i := range b.keys {
		key := b.keys[i]
		value := b.values[i]
		k := string(key)
		if duplicates[k] {
			return nil, errors.New("duplicate key " + k)
		}
		duplicates[k] = true
		oh := hasher.HashIndexFromKey(key)

		buckets[oh].index = oh
		buckets[oh].keys = append(buckets[oh].keys, key)
		buckets[oh].values = append(buckets[oh].values, value)
	}

	// Order buckets by size (retaining the hash index)
	collisions := 0
	sort.Sort(buckets)
nextBucket:
	for i, bucket := range buckets {
		if len(bucket.keys) == 0 {
			continue
		}

		// Check existing hash functions.
		for ri, r := range hasher.r {
			if chdTryHash(hasher, seen, keys, values, indices, &bucket, uint16(ri), r) {
				continue nextBucket
			}
		}

		// Keep trying new functions until we get one that does not collide. The number of retries here is very high to
		// allow a very high probability of not getting collisions.
		for i := 0; i < 10000000; i++ {
			if i > collisions {
				collisions = i
			}
			ri, r := hasher.Generate()
			if chdTryHash(hasher, seen, keys, values, indices, &bucket, ri, r) {
				hasher.Add(r)
				continue nextBucket
			}
		}

		// Failed to find a hash function with no collisions.
		return nil, fmt.Errorf(
			"failed to find a collision-free hash function after ~10000000 attempts, for bucket %d/%d with %d entries: %s",
			i, len(buckets), len(bucket.keys), &bucket)
	}

	// println("max bucket collisions:", collisions)
	// println("keys:", len(table))
	// println("hash functions:", len(hasher.r))

	return &Chd{
		r:       hasher.r,
		indices: indices,
		keys:    keys,
		values:  values,
	}, nil
}

func newChdHasher(size uint64, buckets uint64) *chdHasher {
	rs := rand.NewSource(time.Now().UnixNano())
	c := &chdHasher{size: size, buckets: buckets, rand: rand.New(rs)}
	c.Add(c.random())
	return c
}

func (h *chdHasher) random() uint64 {
	return (uint64(h.rand.Uint32()) << 32) | uint64(h.rand.Uint32())
}

// Hash index from key.
func (h *chdHasher) HashIndexFromKey(b []byte) uint64 {
	return (chdHash(b) ^ h.r[0]) % h.buckets
}

// Table hash from random value and key. Generate() returns these random values.
func (h *chdHasher) Table(r uint64, b []byte) uint64 {
	return (chdHash(b) ^ h.r[0] ^ r) % h.size
}

func (h *chdHasher) Generate() (uint16, uint64) {
	return h.Len(), h.random()
}

// Add a random value generated by Generate().
func (h *chdHasher) Add(r uint64) {
	h.r = append(h.r, r)
}

func (h *chdHasher) Len() uint16 {
	return uint16(len(h.r))
}

func (h *chdHasher) String() string {
	return fmt.Sprintf("chdHasher{size: %d, buckets: %d, r: %v}", h.size, h.buckets, h.r)
}
