# Copyright (c) 2016, Daniel Martí. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided with the distribution.
# * Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#   products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import copy

from omlish import dataclasses as dc

from .nodes import Lit
from .nodes import Word
from .nodes import BraceExp


##


LIT_LEFT_BRACE  = Lit(value="{")
LIT_COMMA       = Lit(value=",")
LIT_DOTS        = Lit(value="..")
LIT_RIGHT_BRACE = Lit(value="}")


# SplitBraces parses brace expansions within a word's literal parts.
# If any valid brace expansions are found, they are replaced with BraceExp nodes,
# and the function returns True.
# Otherwise, the word is left untouched and the function returns False.
#
# For example, a literal word "foo{bar,baz}" will result in a word containing
# the literal "foo", and a brace expansion with the elements "bar" and "baz".
#
# It does not return an error; malformed brace expansions are simply skipped.
# For example, the literal word "a{b" is left unchanged.
def split_braces(word: Word) -> bool:
    if not any(isinstance(part, Lit) and '{' in part.value for part in word.parts):
        # In the common case where a word has no braces, skip any allocs.
        return False

    top = Word()
    acc = top
    cur: BraceExp | None = None
    opn: list[BraceExp] = []

    def pop() -> BraceExp:
        nonlocal acc
        nonlocal cur
        nonlocal opn
        old = cur
        opn = opn[:-1]
        if len(opn) == 0:
            cur = None
            acc = top
        else:
            cur = opn[-1]
            acc = cur.elems[-1]
        return old

    def add_lit(lit: Lit) -> None:
        acc.parts.append(lit)

    for wp in word.parts:
        if not isinstance(wp, Lit):
            acc.parts.append(wp)
            continue
        lit = wp

        last = 0
        j = -1
        while True:
            j += 1
            if j >= len(lit.value):
                break

            def add_lit_idx() -> None:
                if last == j:
                    return  # empty lit
                l2 = copy.copy(lit)
                l2.value = l2.value[last:j]
                add_lit(l2)
                
            if lit.value[j] == '{':
                add_lit_idx()
                acc = Word()
                cur = BraceExp(elems=[acc])
                opn.append(cur)
                
            elif lit.value[j] == ',':
                if cur is None:
                    continue
                add_lit_idx()
                acc = Word()
                cur.elems.append(acc)
                
            elif lit.value[j] == '.':
                if cur is None:
                    continue
                if j+1 >= len(lit.value) or lit.value[j+1] != '.':
                    continue
                add_lit_idx()
                cur.sequence = True
                acc = Word()
                cur.elems.append(acc)
                j += 1
                
            elif lit.value[j] == '}':
                if cur is None:
                    continue
                add_lit_idx()
                
                br = pop()
                if len(br.elems) == 1:
                    # return {x} to a non-brace
                    add_lit(LIT_LEFT_BRACE)
                    acc.parts.extend(br.elems[0].parts)
                    add_lit(LIT_RIGHT_BRACE)
                    break
                    
                if not br.sequence:
                    acc.parts.append(br)
                    break
                    
                chars = [False, False]
                broken = False
                for i, elem in enumerate(br.elems[:2]):
                    val = elem.lit()
                    try:
                        int(val)  # noqa
                    except ValueError:
                        if len(val) == 1 and ascii_letter(val[0]):
                            chars[i] = True
                        else:
                            broken = True
                        
                if len(br.elems) == 3:
                    # increment must be a number
                    val = br.elems[2].lit()
                    try:
                        int(val)  # noqa
                    except ValueError:
                        broken = True
                        
                # are start and end both chars or
                # non-chars?
                if chars[0] != chars[1]:
                    broken = True
                if not broken:
                    acc.parts.append(br)
                    break

                # return broken {x..y[..incr]} to a non-brace
                add_lit(LIT_LEFT_BRACE)
                for i, elem in enumerate(br.elems):
                    if i > 0:
                        add_lit(LIT_DOTS)
                    acc.parts.extend(elem.parts)
                add_lit(LIT_RIGHT_BRACE)
                
            else:
                continue
                
            last = j + 1
            
        if last == 0:
            add_lit(lit)
        else:
            left = copy.copy(lit)
            left.value = left.value[last:]
            add_lit(left)
            
    # open braces that were never closed fall back to non-braces
    while acc != top:
        br = pop()
        add_lit(LIT_LEFT_BRACE)
        for i, elem in enumerate(br.elems):
            if i > 0:
                if br.sequence:
                    add_lit(LIT_DOTS)
                else:
                    add_lit(LIT_COMMA)
            acc.parts.extend(elem.parts)

    for fld in dc.fields(Word):
        setattr(word, fld.name, getattr(top, fld.name))
    return True
