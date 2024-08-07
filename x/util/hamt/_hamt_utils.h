// PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
// --------------------------------------------
//
// 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
//    ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
//    documentation.
//
// 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
//    royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
//    works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's
//    License Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001-2024 Python Software Foundation; All
//    Rights Reserved" are retained in Python alone or in any derivative version prepared by Licensee.
//
// 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
//    wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include
//    in any such work a brief summary of the changes made to Python.
//
// 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
//    EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR
//    WARRANTY OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY
//    THIRD PARTY RIGHTS.
//
// 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
//    DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN
//    IF ADVISED OF THE POSSIBILITY THEREOF.
//
// 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
//
// 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
//    venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
//    name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
//
// 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
//    License Agreement.

// https://github.com/python/cpython/blob/4767a6e31c0550836b2af45d27e374e721f0c4e6/Include/internal/pycore_bitutils.h#L95

#pragma once

// Population count: count the number of 1's in 'x'
// (number of bits set to 1), also known as the hamming weight.
//
// Implementation note. CPUID is not used, to test if x86 POPCNT instruction
// can be used, to keep the implementation simple. For example, Visual Studio
// __popcnt() is not used this reason. The clang and GCC builtin function can
// use the x86 POPCNT instruction if the target architecture has SSE4a or
// newer.
static inline int
_Py_popcount32(uint32_t x)
{
#if (defined(__clang__) || defined(__GNUC__))

#if SIZEOF_INT >= 4
    Py_BUILD_ASSERT(sizeof(x) <= sizeof(unsigned int));
    return __builtin_popcount(x);
#else
    // The C standard guarantees that unsigned long will always be big enough
    // to hold a uint32_t value without losing information.
    Py_BUILD_ASSERT(sizeof(x) <= sizeof(unsigned long));
    return __builtin_popcountl(x);
#endif

#else
    // 32-bit SWAR (SIMD Within A Register) popcount

    // Binary: 0 1 0 1 ...
    const uint32_t M1 = 0x55555555;
    // Binary: 00 11 00 11. ..
    const uint32_t M2 = 0x33333333;
    // Binary: 0000 1111 0000 1111 ...
    const uint32_t M4 = 0x0F0F0F0F;

    // Put count of each 2 bits into those 2 bits
    x = x - ((x >> 1) & M1);
    // Put count of each 4 bits into those 4 bits
    x = (x & M2) + ((x >> 2) & M2);
    // Put count of each 8 bits into those 8 bits
    x = (x + (x >> 4)) & M4;
    // Sum of the 4 byte counts.
    // Take care when considering changes to the next line. Portability and
    // correctness are delicate here, thanks to C's "integer promotions" (C99
    // §6.3.1.1p2). On machines where the `int` type has width greater than 32
    // bits, `x` will be promoted to an `int`, and following C's "usual
    // arithmetic conversions" (C99 §6.3.1.8), the multiplication will be
    // performed as a multiplication of two `unsigned int` operands. In this
    // case it's critical that we cast back to `uint32_t` in order to keep only
    // the least significant 32 bits. On machines where the `int` type has
    // width no greater than 32, the multiplication is of two 32-bit unsigned
    // integer types, and the (uint32_t) cast is a no-op. In both cases, we
    // avoid the risk of undefined behaviour due to overflow of a
    // multiplication of signed integer types.
    return (uint32_t)(x * 0x01010101U) >> 24;
#endif
}
