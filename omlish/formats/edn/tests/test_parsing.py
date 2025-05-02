# https://github.com/jorinvo/edn-data/blob/1e5824f63803eb58f35e98839352000053d47115/test/parse.test.ts
import datetime

from ..parsing import parse
from ..values import Char
from ..values import Keyword
from ..values import List
from ..values import Map
from ..values import Set
from ..values import Symbol
from ..values import TaggedVal
from ..values import Vector


def test_empty_document_as_null():
    assert parse('') is None
    assert parse('; just some comment') is None


def test_empty_string():
    assert parse('""') == ''


def test_string():
    assert parse('"hi"') == 'hi'


def test_string_with_space():
    assert parse('"hi there"') == 'hi there'


def test_string_multiline():
    assert parse('"one\ntwo"') == 'one\ntwo'


def test_string_with_newline():
    assert parse('"one\\ntwo"') == 'one\ntwo'


def test_string_with_windows_newline():
    assert parse('"one\\rtwo"') == 'one\rtwo'


def test_string_with_tab():
    assert parse('"one\\ttwo"') == 'one\ttwo'


def test_string_with_backslash():
    assert parse('"\\\\"') == '\\'


def test_string_with_quote_symbol():
    assert parse('"\\""') == '"'


def test_string_after_symbol_without_space():
    assert parse('[hi"hi"]') == Vector((Symbol('hi'), 'hi'))


def test_string_before_symbol_without_space():
    assert parse('["hi"hi]') == Vector(('hi', Symbol('hi')))


def test_string_after_bool_without_space():
    assert parse('[true"hi"]') == Vector((True, 'hi'))


def test_string_before_bool_without_space():
    assert parse('["hi"true]') == Vector(('hi', True))


def test_string_after_int_without_space():
    assert parse('[123"hi"]') == Vector((123, 'hi'))


def test_string_before_int_without_space():
    assert parse('["hi"123]') == Vector(('hi', 123))


def test_string_after_string_without_space():
    assert parse('["hi""hi"]') == Vector(('hi', 'hi'))


def test_string_before_string_without_space():
    assert parse('["hi""hi"]') == Vector(('hi', 'hi'))


def test_char():
    assert parse('\\a') == Char('a')


def test_char_space():
    assert parse('\\space') == Char(' ')


def test_char_newline():
    assert parse('\\newline') == Char('\n')


def test_char_return():
    assert parse('\\return') == Char('\r')


def test_char_tab():
    assert parse('\\tab') == Char('\t')


def test_char_backslash():
    assert parse('\\\\') == Char('\\')


def test_char_as_string():
    assert parse('\\abc', char_maker=str) == 'abc'


def test_int():
    assert parse('928764') == 928764


def test_int_with_zeros():
    assert parse('1001') == 1001


def test_zero():
    assert parse('0') == 0


def test_plus_int():
    assert parse('+3') == 3


def test_minus_zero():
    assert parse('-0') == -0


def test_minus_int():
    assert parse('-12') == -12


def test_float():
    assert parse('928.764') == 928.764


def test_float_with_zeros():
    assert parse('1001.1') == 1001.1


def test_minus_float():
    assert parse('-8.74') == -8.74


def test_float_e():
    assert parse('2.1e5') == 210000


def test_float_E():  # noqa
    assert parse('2.1E5') == 210000


def test_float_e_plus():
    assert parse('22.1e+2') == 2210


def test_float_E_plus():  # noqa
    assert parse('22.1E+2') == 2210


def test_float_e_minus():
    assert parse('5.12e-3') == 0.00512


def test_float_E_minus():  # noqa
    assert parse('5.12E-3') == 0.00512


def test_float_e_with_zeros():
    assert parse('1001.00100e10') == 10010010000000


def test_bigint_plus():
    assert parse('1234578901234567890124356780123456789N') == 1234578901234567890124356780123456789


def test_bigint_minus():
    assert parse('-1234578901234567890124356780123456789N') == -1234578901234567890124356780123456789


def test_nil():
    assert parse('nil') is None


def test_true():
    assert parse('true') is True


def test_false():
    assert parse('false') is False


def test_symbol_with_single_char():
    assert parse('=') == Symbol('=')


def test_symbol_with_multiple_chars():
    assert parse('even?') == Symbol('even?')


def test_symbol_with_space_after():
    assert parse('even? ') == Symbol('even?')


def test_keyword_with_single_char():
    assert parse(':a') == Keyword('a')


def test_keyword_with_multiple_chars():
    assert parse(':name') == Keyword('name')


def test_keyword_with_space_after():
    assert parse(':ns.nested/name ') == Keyword('ns.nested/name')


def test_empty_vector():
    assert parse('[]') == Vector(())


def test_empty_vector_with_space():
    assert parse('[  ]') == Vector(())


def test_vector_with_single_string():
    assert parse('["one"]') == Vector(('one',))


def test_vector_of_strings():
    assert parse('["one" "and two"]') == Vector(('one', 'and two'))


def test_vector_of_booleans():
    assert parse('[true true]') == Vector((True, True))


def test_vector_with_string_and_bool():
    assert parse('[true "well, then."]') == Vector((True, 'well, then.'))


def test_vector_with_vectors():
    assert parse('[true  ["one" ["two", nil ]]]') == Vector((True, Vector(('one', Vector(('two', None))))))


def test_vector_of_vectors():
    assert parse('[[] [] ]') == Vector((Vector(()), Vector(())))


def test_vector_of_vectors_without_spaces():
    assert parse('[[][]]') == Vector((Vector(()), Vector(())))


def test_vector_after_symbol_without_space():
    assert parse('[hi[]]') == Vector((Symbol('hi'), Vector(())))


def test_vector_before_symbol_without_space():
    assert parse('[[]hi]') == Vector((Vector(()), Symbol('hi')))


def test_vector_after_bool_without_space():
    assert parse('[true[]]') == Vector((True, Vector(())))


def test_vector_before_bool_without_space():
    assert parse('[[]true]') == Vector((Vector(()), True))


def test_vector_after_string_without_space():
    assert parse('["hi"[]]') == Vector(('hi', Vector(())))


def test_vector_before_string_without_space():
    assert parse('[[]"hi"]') == Vector((Vector(()), 'hi'))


def test_vector_after_vector_without_space():
    assert parse('[[][]]') == Vector((Vector(()), Vector(())))


def test_vector_before_vector_without_space():
    assert parse('[[][]]') == Vector((Vector(()), Vector(())))


def test_empty_list():
    assert parse('()') == List(())


def test_empty_list_with_space():
    assert parse('(  )') == List(())


def test_list_with_single_string():
    assert parse('("one")') == List(('one',))


def test_list_of_strings():
    assert parse('("one" "and two")') == List(('one', 'and two'))


def test_list_of_booleans():
    assert parse('(true true)') == List((True, True))


def test_list_with_string_and_bool():
    assert parse('(true "well, then.")') == List((True, 'well, then.'))


def test_list_of_lists():
    assert parse('(true  ("one" ("two", nil )))') == List((
        True,
        List(('one', List(('two', None)))),
    ))


def test_list_after_symbol_without_space():
    assert parse('(hi())') == List((Symbol('hi'), List(())))


def test_list_before_symbol_without_space():
    assert parse('(()hi)') == List((List(()), Symbol('hi')))


def test_list_after_bool_without_space():
    assert parse('(false())') == List((False, List(())))


def test_list_before_bool_without_space():
    assert parse('(()false)') == List((List(()), False))


def test_list_after_string_without_space():
    assert parse('("hi"())') == List(('hi', List(())))


def test_list_before_string_without_space():
    assert parse('(()"hi")') == List((List(()), 'hi'))


def test_list_as_array():
    assert parse('(true  ("one" ("two", nil )))', list_maker=list) == [True, ['one', ['two', None]]]


def test_empty_set():
    assert parse('#{}') == Set(())


def test_empty_set_with_space():
    assert parse('#{  }') == Set(())


def test_set_with_single_string():
    assert parse('#{"one"}') == Set(('one',))


def test_set_of_strings():
    assert parse('#{"one" "and two"}') == Set(('one', 'and two'))


def test_set_of_booleans():
    assert parse('#{true true}') == Set((True, True))


def test_set_with_string_and_bool():
    assert parse('#{true "well, then."}') == Set((True, 'well, then.'))


def test_set_of_sets():
    assert parse('#{true  #{"one" #{"two", nil }}}') == Set((True, Set(('one', Set(('two', None))))))


def test_set_as_array():
    assert parse('#{true  #{"one" #{"two", nil }}}', set_maker=list) == [True, ['one', ['two', None]]]


def test_set_as_set():
    result = parse('#{true  #{"one" #{"two", nil }}}', set_maker=frozenset)
    # Since set ordering is not guaranteed, we need to check membership
    assert isinstance(result, frozenset)
    assert True in result

    inner_sets = [item for item in result if isinstance(item, frozenset)]
    assert len(inner_sets) == 1
    inner_set = inner_sets[0]

    assert 'one' in inner_set

    inner_inner_sets = [item for item in inner_set if isinstance(item, frozenset)]
    assert len(inner_inner_sets) == 1
    inner_inner_set = inner_inner_sets[0]

    assert 'two' in inner_inner_set
    assert None in inner_inner_set


def test_set_after_symbol_without_space():
    assert parse('#{hi#{}}') == Set((Symbol('hi'), Set(())))


def test_set_before_symbol_without_space():
    assert parse('#{#{}hi}') == Set((Set(()), Symbol('hi')))


def test_set_after_bool_without_space():
    assert parse('#{true#{}}') == Set((True, Set(())))


def test_set_before_bool_without_space():
    assert parse('#{#{}true}') == Set((Set(()), True))


def test_set_after_string_without_space():
    assert parse('#{"hi"#{}}') == Set(('hi', Set(())))


def test_set_before_string_without_space():
    assert parse('#{#{}"hi"}') == Set((Set(()), 'hi'))


def test_empty_map():
    assert parse('{}') == Map(())


def test_empty_map_with_space():
    assert parse('{  }') == Map(())


def test_map_with_single_string():
    assert parse('{"one" "two"}') == Map((('one', 'two'),))


def test_map_of_two():
    result = parse('{"a" true, "b" false }')
    assert isinstance(result, Map)
    assert len(result.map) == 2
    # Check both key-value pairs exist
    assert ('a', True) in result.map
    assert ('b', False) in result.map


def test_map_of_maps():
    assert parse('{true  {"one" {"two", nil }}}') == Map(((True, Map((('one', Map((('two', None),))),))),))


def test_map_as_object():
    assert parse('{"a"  {"b" {"c", 123}}}', map_maker=dict) == {'a': {'b': {'c': 123}}}


def test_map_as_map():
    result = parse('{"a"  {"b" {"c", 123}}}', map_maker=dict)
    assert isinstance(result, dict)
    assert 'a' in result
    assert isinstance(result['a'], dict)
    assert 'b' in result['a']
    assert isinstance(result['a']['b'], dict)
    assert 'c' in result['a']['b']
    assert result['a']['b']['c'] == 123


def test_map_after_symbol_without_space():
    assert parse('{hi{}}') == Map(((Symbol('hi'), Map(())),))


def test_map_before_symbol_without_space():
    assert parse('{{}hi}') == Map(((Map(()), Symbol('hi')),))


def test_map_after_bool_without_space():
    assert parse('{false{}}') == Map(((False, Map(())),))


def test_map_before_bool_without_space():
    assert parse('{{}false}') == Map(((Map(()), False),))


def test_map_after_string_without_space():
    assert parse('{"hi"{}}') == Map((('hi', Map(())),))


def test_map_before_string_without_space():
    assert parse('{{}"hi"}') == Map(((Map(()), 'hi'),))


def test_comment():
    assert parse('; "hi"') is None


def test_ignore_comments():
    assert parse("""
      ; look at this
      ""
      ;; nice, isn't it?
    """) == ''


def test_tagged_key():
    assert parse('#ns.a/tag :key') == TaggedVal('ns.a/tag', Keyword('key'))


def test_tagged_int():
    assert parse('#my/tag 555') == TaggedVal('my/tag', 555)


def test_tag_tagged_value():
    assert parse('#ns.a/tag2 #ns.a/tag1 :key') == TaggedVal('ns.a/tag2', TaggedVal('ns.a/tag1', Keyword('key')))


def test_tag_tagged_value_nested():
    assert parse('(:a [#ns.a/tag2 #ns.a/tag1 :key "hi"] 1)') == List((
        Keyword('a'),
        Vector((
            TaggedVal(
                'ns.a/tag2',
                TaggedVal(
                    'ns.a/tag1',
                    Keyword('key'),
                ),
            ),
            'hi',
        )),
        1,
    ))


def test_custom_tag_handler():
    def my_tag_handler(val):
        if not isinstance(val, int):
            raise ValueError('not a number')  # noqa
        return val * 2

    assert parse('#my/tag 5', tag_handlers={'my/tag': my_tag_handler}) == 10


def test_inst_as_date():
    assert parse('#inst "2020-04-12T21:39:15.482Z"') == \
           datetime.datetime(2020, 4, 12, 21, 39, 15, 482000, tzinfo=datetime.UTC)


def test_discard_string():
    assert parse('#_"hi"') is None
    assert parse('#_  "hi"') is None


def test_discard_int():
    assert parse('#_928764') is None
    assert parse('#_  928764') is None


def test_discard_symbol():
    assert parse('#_even? ') is None
    assert parse('#_  even? ') is None


def test_discard_keyword():
    assert parse('#_:a') is None
    assert parse('#_  :a') is None


def test_discard_vector():
    assert parse('#_[]') is None
    assert parse('#_  []') is None


def test_discard_list():
    assert parse('#_()') is None
    assert parse('#_  ()') is None


def test_discard_set():
    assert parse('#_#{}') is None
    assert parse('#_  #{}') is None


def test_discard_map():
    assert parse('#_{}') is None
    assert parse('#_  {}') is None


def test_discard_vector_element():
    assert parse('[1 #_2 3]') == Vector((1, 3))
    assert parse('[1 #_  2 3]') == Vector((1, 3))


def test_discard_list_element():
    assert parse('(1 #_2 3)') == List((1, 3))
    assert parse('(1 #_  2 3)') == List((1, 3))


def test_discard_set_element():
    result = parse('#{1 #_2 3}')
    assert isinstance(result, Set)
    assert len(result.items) == 2
    assert 1 in result.items
    assert 3 in result.items


def test_discard_map_middle_element():
    assert parse('{1 #_2 3}') == Map(((1, 3),))
    assert parse('{1 #_  2 3}') == Map(((1, 3),))


def test_discard_map_last_element():
    assert parse('{1 2 #_3}') == Map(((1, 2),))
    assert parse('{1 2 #_  3}') == Map(((1, 2),))


def test_discard_tag():
    assert parse('#_  #ns.a/tag :key') is None
    assert parse('#_#ns.a/tag :key') is None


def test_multiple_discards():
    assert parse('#_ #_ #_ 1 2 3') is None


def test_crux_tx_response():
    result = parse('{:crux.tx/tx-id 2, :crux.tx/tx-time #inst "2020-04-13T08:01:14.261-00:00"}')
    assert isinstance(result, Map)
    assert len(result.map) == 2

    key_vals = {k.s if isinstance(k, Keyword) else k: v for k, v in result.map}
    assert 'crux.tx/tx-id' in key_vals
    assert key_vals['crux.tx/tx-id'] == 2

    assert 'crux.tx/tx-time' in key_vals
    assert isinstance(key_vals['crux.tx/tx-time'], datetime.datetime)
    assert key_vals['crux.tx/tx-time'] == datetime.datetime(2020, 4, 13, 8, 1, 14, 261000, tzinfo=datetime.UTC)


def test_crux_tx_response_as_object():
    result = parse(
        '{:crux.tx/tx-id 2, :crux.tx/tx-time #inst "2020-04-13T08:01:14.261-00:00"}',
        map_maker=dict,
        keyword_maker=str,
    )
    assert isinstance(result, dict)
    assert 'crux.tx/tx-id' in result
    assert result['crux.tx/tx-id'] == 2
    assert 'crux.tx/tx-time' in result
    assert isinstance(result['crux.tx/tx-time'], datetime.datetime)
    assert result['crux.tx/tx-time'] == datetime.datetime(2020, 4, 13, 8, 1, 14, 261000, tzinfo=datetime.UTC)


def test_readme_example():
    result1 = parse('{:key "value" :list [1 2 3]}')
    assert isinstance(result1, Map)
    assert len(result1.map) == 2

    found_key_value = False
    found_list_value = False

    for k, v in result1.map:
        if isinstance(k, Keyword) and k.s == 'key':
            assert v == 'value'
            found_key_value = True
        elif isinstance(k, Keyword) and k.s == 'list':
            assert v == Vector((1, 2, 3))
            found_list_value = True

    assert found_key_value and found_list_value

    result2 = parse(
        '{:key "value" :list [1 2 3]}',
        map_maker=dict,
        keyword_maker=str,
        vector_maker=list,
    )
    assert result2 == {
        'key': 'value',
        'list': [1, 2, 3],
    }


def test_object_keys():
    result = parse('{[407 {:someKey "lovely-value"}] #{123}}')

    assert result == Map(((Vector((407, Map(((Keyword('someKey'), 'lovely-value'),)))), Set((123,))),))
