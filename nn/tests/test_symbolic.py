from ..symbolic import Lt
from ..symbolic import Mul
from ..symbolic import Num
from ..symbolic import Sum
from ..symbolic import Var
from ..symbolic import and_
from ..symbolic import sum_
from ..symbolic import var


##


def _test_variable(v, n, m, s):
    assert v.expr == s
    assert v.min == n
    assert v.max == m


def test_dispatch():
    from ..symbolic import SymRenderer
    from ..symbolic import DebugSymRenderer

    v = Var('a', 3, 8) >= 8
    for _ in range(2):
        assert SymRenderer().render(v) == '((a*-1)<-7)'
        assert DebugSymRenderer().render(v) == '((a[3,8]*-1)<-7)'


class TestSymbolic:
    def test_symbolic(self):
        idx1 = Var('idx1', 0, 3)
        idx2 = Var('idx2', 0, 3)
        assert idx1 == idx1
        assert idx1 != idx2

    def test_ge(self):
        _test_variable(Var('a', 3, 8) >= 77, 0, 0, '0')
        _test_variable(Var('a', 3, 8) >= 9, 0, 0, '0')
        _test_variable(Var('a', 3, 8) >= 8, 0, 1, '((a*-1)<-7)')
        _test_variable(Var('a', 3, 8) >= 4, 0, 1, '((a*-1)<-3)')
        _test_variable(Var('a', 3, 8) >= 3, 1, 1, '1')
        _test_variable(Var('a', 3, 8) >= 2, 1, 1, '1')

    def test_lt(self):
        _test_variable(Var('a', 3, 8) < 77, 1, 1, '1')
        _test_variable(Var('a', 3, 8) < 9, 1, 1, '1')
        _test_variable(Var('a', 3, 8) < 8, 0, 1, '(a<8)')
        _test_variable(Var('a', 3, 8) < 4, 0, 1, '(a<4)')
        _test_variable(Var('a', 3, 8) < 3, 0, 0, '0')
        _test_variable(Var('a', 3, 8) < 2, 0, 0, '0')

    def test_ge_divides(self):
        expr = (Var('idx', 0, 511) * 4 + Var('FLOAT4_INDEX', 0, 3)) < 512
        _test_variable(expr, 0, 1, '((idx*4)<512)')
        _test_variable(expr // 4, 0, 1, '(idx<128)')

    def test_ge_divides_and(self):
        expr = and_([
            (Var('idx1', 0, 511) * 4 + Var('FLOAT4_INDEX', 0, 3)) < 512,
            (Var('idx2', 0, 511) * 4 + Var('FLOAT4_INDEX', 0, 3)) < 512,
        ])
        _test_variable(expr // 4, 0, 1, '((idx1<128) and (idx2<128))')
        expr = and_([
            (Var('idx1', 0, 511) * 4 + Var('FLOAT4_INDEX', 0, 3)) < 512,
            (Var('idx2', 0, 511) * 4 + Var('FLOAT8_INDEX', 0, 7)) < 512,
        ])
        _test_variable(expr // 4, 0, 1, '((((FLOAT8_INDEX//4)+idx2)<128) and (idx1<128))')

    def test_lt_factors(self):
        expr = and_([(Var('idx1', 0, 511) * 4 + Var('FLOAT4_INDEX', 0, 256)) < 512])
        _test_variable(expr, 0, 1, '(((idx1*4)+FLOAT4_INDEX)<512)')

    def test_div_becomes_num(self):
        assert isinstance(Var('a', 2, 3) // 2, Num)

    def test_var_becomes_num(self):
        assert isinstance(var('a', 2, 2), Num)

    def test_equality(self):
        idx1 = Var('idx1', 0, 3)
        idx2 = Var('idx2', 0, 3)
        assert idx1 == idx1
        assert idx1 != idx2
        assert idx1 * 4 == idx1 * 4
        assert idx1 * 4 != idx1 * 3
        assert idx1 * 4 != idx1 + 4
        assert idx1 * 4 != idx2 * 4
        assert idx1 + idx2 == idx1 + idx2
        assert idx1 + idx2 == idx2 + idx1
        assert idx1 + idx2 != idx2

    def test_factorize(self):
        a = Var('a', 0, 8)
        _test_variable(a * 2 + a * 3, 0, 8 * 5, '(a*5)')

    def test_factorize_no_mul(self):
        a = Var('a', 0, 8)
        _test_variable(a + a * 3, 0, 8 * 4, '(a*4)')

    def test_neg(self):
        _test_variable(-Var('a', 0, 8), -8, 0, '(a*-1)')

    def test_add_1(self):
        _test_variable(Var('a', 0, 8) + 1, 1, 9, '(1+a)')

    def test_add_num_1(self):
        _test_variable(Var('a', 0, 8) + Num(1), 1, 9, '(1+a)')

    def test_sub_1(self):
        _test_variable(Var('a', 0, 8) - 1, -1, 7, '(-1+a)')

    def test_sub_num_1(self):
        _test_variable(Var('a', 0, 8) - Num(1), -1, 7, '(-1+a)')

    def test_mul_0(self):
        _test_variable(Var('a', 0, 8) * 0, 0, 0, '0')

    def test_mul_1(self):
        _test_variable(Var('a', 0, 8) * 1, 0, 8, 'a')

    def test_mul_neg_1(self):
        _test_variable((Var('a', 0, 2) * -1) // 3, -1, 0, '((((a*-1)+3)//3)+-1)')

    def test_mul_2(self):
        _test_variable(Var('a', 0, 8) * 2, 0, 16, '(a*2)')

    def test_div_1(self):
        _test_variable(Var('a', 0, 8) // 1, 0, 8, 'a')

    def test_mod_1(self):
        _test_variable(Var('a', 0, 8) % 1, 0, 0, '0')

    def test_add_min_max(self):
        _test_variable(Var('a', 0, 8) * 2 + 12, 12, 16 + 12, '((a*2)+12)')

    def test_div_min_max(self):
        _test_variable(Var('a', 0, 7) // 2, 0, 3, '(a//2)')

    def test_div_neg_min_max(self):
        _test_variable(Var('a', 0, 7) // -2, -3, 0, '((a//2)*-1)')

    def test_sum_div_min_max(self):
        _test_variable(sum_([Var('a', 0, 7), Var('b', 0, 3)]) // 2, 0, 5, '((a+b)//2)')

    def test_sum_div_factor(self):
        _test_variable(sum_([Var('a', 0, 7) * 4, Var('b', 0, 3) * 4]) // 2, 0, 20, '((a*2)+(b*2))')

    def test_sum_div_some_factor(self):
        _test_variable(sum_([Var('a', 0, 7) * 5, Var('b', 0, 3) * 4]) // 2, 0, 23, '(((a*5)//2)+(b*2))')

    def test_sum_div_some_partial_factor(self):
        _test_variable(sum_([Var('a', 0, 7) * 6, Var('b', 0, 7) * 6]) // 16, 0, 5, '(((a*3)+(b*3))//8)')
        _test_variable(sum_([Num(16), Var('a', 0, 7) * 6, Var('b', 0, 7) * 6]) // 16, 1, 6, '((((a*3)+(b*3))//8)+1)')

    def test_sum_div_no_factor(self):
        _test_variable(sum_([Var('a', 0, 7) * 5, Var('b', 0, 3) * 5]) // 2, 0, 25, '(((a*5)+(b*5))//2)')

    def test_mod_factor(self):
        # NOTE: even though the mod max is 50, it can't know this without knowing about the mul
        _test_variable(sum_([Var('a', 0, 7) * 100, Var('b', 0, 3) * 50]) % 100, 0, 99, '((b*50)%100)')

    def test_sum_div_const(self):
        _test_variable(sum_([Var('a', 0, 7) * 4, Num(3)]) // 4, 0, 7, 'a')

    def test_sum_div_const_big(self):
        _test_variable(sum_([Var('a', 0, 7) * 4, Num(3)]) // 16, 0, 1, '(a//4)')

    def test_mod_mul(self):
        _test_variable((Var('a', 0, 5) * 10) % 9, 0, 5, 'a')

    def test_mul_mul(self):
        _test_variable((Var('a', 0, 5) * 10) * 9, 0, 5 * 10 * 9, '(a*90)')

    def test_div_div(self):
        _test_variable((Var('a', 0, 1800) // 10) // 9, 0, 20, '(a//90)')

    def test_distribute_mul(self):
        _test_variable(
            sum_([Var('a', 0, 3), Var('b', 0, 5)]) * 3,
            0,
            24,
            '((a*3)+(b*3))',
        )

    def test_mod_mul_sum(self):
        _test_variable(sum_([Var('b', 0, 2), Var('a', 0, 5) * 10]) % 9, 0, 7, '(a+b)')

    def test_sum_0(self):
        _test_variable(sum_([Var('a', 0, 7)]), 0, 7, 'a')

    def test_mod_remove(self):
        _test_variable(Var('a', 0, 6) % 100, 0, 6, 'a')

    def test_big_mod(self):
        # NOTE: we no longer support negative variables
        # _test_variable(Var('a', -20, 20)%10, -9, 9, '(a%10)')
        # _test_variable(Var('a', -20, 0)%10, -9, 0, '(a%10)')
        # _test_variable(Var('a', -20, 1)%10, -9, 1, '(a%10)')
        _test_variable(Var('a', 0, 20) % 10, 0, 9, '(a%10)')
        # _test_variable(Var('a', -1, 20)%10, -1, 9, '(a%10)')

    def test_gt_remove(self):
        _test_variable(Var('a', 0, 6) >= 25, 0, 0, '0')

    def test_lt_remove(self):
        _test_variable(Var('a', 0, 6) < -3, 0, 0, '0')
        _test_variable(Var('a', 0, 6) < 3, 0, 1, '(a<3)')
        _test_variable(Var('a', 0, 6) < 8, 1, 1, '1')

    def test_and_fold(self):
        _test_variable(and_([Num(0), Var('a', 0, 1)]), 0, 0, '0')

    def test_and_remove(self):
        _test_variable(and_([Num(1), Var('a', 0, 1)]), 0, 1, 'a')

    def test_mod_factor_negative(self):
        _test_variable(sum_([Num(-29), Var('a', 0, 10), Var('b', 0, 10) * 28]) % 28, 0, 27, '((27+a)%28)')
        _test_variable(sum_([Num(-29), Var('a', 0, 100), Var('b', 0, 10) * 28]) % 28, 0, 27, '((27+a)%28)')

    def test_sum_combine_num(self):
        _test_variable(sum_([Num(29), Var('a', 0, 10), Num(-23)]), 6, 16, '(6+a)')

    def test_sum_num_hoisted_and_factors_cancel_out(self):
        _test_variable(sum_([Var('a', 0, 1) * -4 + 1, Var('a', 0, 1) * 4]), 1, 1, '1')

    def test_div_factor(self):
        _test_variable(sum_([Num(-40), Var('a', 0, 10) * 2, Var('b', 0, 10) * 40]) // 40, -1, 9, '(-1+b)')

    def test_mul_div(self):
        _test_variable((Var('a', 0, 10) * 4) // 4, 0, 10, 'a')

    def test_mul_div_factor_mul(self):
        _test_variable((Var('a', 0, 10) * 8) // 4, 0, 20, '(a*2)')

    def test_mul_div_factor_div(self):
        _test_variable((Var('a', 0, 10) * 4) // 8, 0, 5, '(a//2)')

    def test_div_remove(self):
        _test_variable(sum_([Var('idx0', 0, 127) * 4, Var('idx2', 0, 3)]) // 4, 0, 127, 'idx0')

    def test_div_numerator_negative(self):
        _test_variable((Var('idx', 0, 9) * -10) // 11, -9, 0, '((((idx*-10)+99)//11)+-9)')

    def test_div_into_mod(self):
        _test_variable((Var('idx', 0, 16) * 4) % 8 // 4, 0, 1, '(idx%2)')


def _test_numeric(f):
    # TODO: why are the negative tests broken? (even if we did support negative variables)
    # mn, mx = -10, 10
    mn, mx = 0, 10
    # one number
    for i in range(mn, mx):
        v = f(Num(i))
        # print(i, f(i), v.min, v.max)
        assert v.min == v.max
        assert v.min == f(i)
    for kmin in range(mn, mx):
        for kmax in range(mn, mx):
            if kmin > kmax:
                continue
            v = f(var('tmp', kmin, kmax))
            values = [f(rv) for rv in range(kmin, kmax + 1)]
            # the min and max may not be exact
            assert v.min <= min(values)
            assert v.max >= max(values)


class TestSymbolicNumeric:
    def test_mod_4(self):
        _test_numeric(lambda x: (x % 4))

    def test_div_4(self):
        _test_numeric(lambda x: (x // 4))

    def test_plus_1_div_2(self):
        _test_numeric(lambda x: (x + 1) // 2)

    def test_plus_1_mod_2(self):
        _test_numeric(lambda x: (x + 1) % 2)

    def test_times_2(self):
        _test_numeric(lambda x: x * 2)

    def test_times_2_plus_3(self):
        _test_numeric(lambda x: x * 2 + 3)

    def test_times_2_plus_3_mod_4(self):
        _test_numeric(lambda x: (x * 2 + 3) % 4)

    def test_times_2_plus_3_div_4(self):
        _test_numeric(lambda x: (x * 2 + 3) // 4)

    def test_times_2_plus_3_div_4_mod_4(self):
        _test_numeric(lambda x: ((x * 2 + 3) // 4) % 4)


class TestSymbolicVars:
    def test_simple(self):
        z = Num(0)
        a = Var('a', 0, 10)
        b = Var('b', 0, 10)
        c = Var('c', 0, 10)
        assert z.vars() == z.vars() == []
        assert a.vars() == a.vars() == [a]
        m = Mul.new(a, 3)
        assert m.vars() == [a]
        s = Sum.new([a, b, c])
        assert s.vars() == [a, b, c]

    def test_compound(self):
        a = Var('a', 0, 10)
        b = Var('b', 0, 10)
        c = Var('c', 0, 10)
        assert (a + b * c).vars() == [a, b, c]
        assert (a % 3 + b // 5).vars() == [a, b]
        assert (a + b + c - a).vars() == [b, c]


class TestSymbolicMinMax:
    def test_min_max_known(self):
        a = Var('a', 1, 8)
        assert max(1, a) == max(a, 1) == a
        assert min(1, a) == min(a, 1) == 1


class TestSymRender:
    def test_sym_render(self):
        a = Var('a', 1, 8)
        b = Var('b', 1, 10)
        assert sym_render(a) == 'a'
        assert sym_render(1) == '1'
        assert sym_render(a + 1) == '(1+a)'
        assert sym_render(a * b) == '(a*b)'


class TestSymbolicSymbolicOps:
    def test_sym_div_sym(self):
        i = Var('i', 1, 10)
        idx0 = Var('idx0', 0, i * 3 - 1)
        assert Num(0) // (Var('i', 1, 10) * 128) == 0
        assert Num(127) // (Var('i', 1, 10) * 128) == 0
        assert idx0 // (i * 3) == 0

    def test_sym_mod_sym(self):
        i = Var('i', 1, 10)
        idx0 = Var('idx0', 0, i * 3 - 1)
        assert Num(0) % (Var('i', 1, 10) * 128) == 0
        assert Num(127) % (Var('i', 1, 10) * 128) == 127
        assert Num(128) % (Var('i', 1, 10) * 128 + 128) == 128
        assert 0 % (Var('i', 1, 10) * 128) == 0
        assert 127 % (Var('i', 1, 10) * 128) == 127
        assert 128 % (Var('i', 1, 10) * 128 + 128) == 128
        assert idx0 % (i * 3) == idx0
        assert i % i == 0

    def test_mulsym_divmod_sym(self):
        i = Var('i', 1, 10)
        idx0 = Var('idx0', 0, 31)
        assert (idx0 * (i * 4 + 4)) // (i + 1) == (idx0 * 4)
        assert (idx0 * (i * 4 + 4)) % (i + 1) == 0
        assert (idx0 * i) % i == 0

    def test_sumsym_divmod_sumsym(self):
        i = Var('i', 1, 10)
        idx0 = Var('idx0', 0, 7)
        idx1 = Var('idx1', 0, 3)
        idx2 = Var('idx2', 0, i)
        assert (idx0 * (i * 4 + 4) + idx1 * (i + 1) + idx2) // (i + 1) == idx0 * 4 + idx1
        assert (idx0 * (i * 4 + 4) + idx1 * (i + 1) + idx2) % (i + 1) == idx2
        assert (i + 1) % (i * 128 + 128) == (i + 1)

    def test_sym_lt_sym(self):
        a = Var('a', 1, 5)
        b = Var('b', 6, 9)
        c = Var('c', 1, 10)
        # if the value is always the same, it folds to num
        assert a < b
        # if it remains as a LtSym, bool is always true and we need to test against min to test if it always evals to
        # True
        assert isinstance(a < c, Lt) and (a < c).min == 0 and (a < c).max == 1
        assert a < c
        assert not (a < c).min
        assert isinstance(a > c, Lt) and (a > c).min == 0 and (a > c).max == 1
        assert not (a > c).min
        # same when comparing with a constant
        assert a < 3
        assert a > 3

    def test_num_sym_mul_sym(self):
        a = Num(2)
        b = Var('b', 1, 5)
        c = a * b
        assert c == b * 2
        assert isinstance(c, Mul)
