# flake8: noqa: E241
# ruff: noqa: SLF001
# @omlish-precheck-allow-any-unicode
# Copyright (C) 2012-2020 Janne Vanhala
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# https://github.com/jpvanhal/inflection/tree/88eefaacf7d0caaa701af7c8ab2d0ab3f17086f1
import typing as ta

import pytest

from .. import inflect


TestParameters: ta.TypeAlias = tuple[tuple[str, str], ...]


SINGULAR_TO_PLURAL: TestParameters = (
    ('search', 'searches'),
    ('switch', 'switches'),
    ('fix', 'fixes'),
    ('box', 'boxes'),
    ('process', 'processes'),
    ('address', 'addresses'),
    ('case', 'cases'),
    ('stack', 'stacks'),
    ('wish', 'wishes'),
    ('fish', 'fish'),
    ('jeans', 'jeans'),
    ('funky jeans', 'funky jeans'),

    ('category', 'categories'),
    ('query', 'queries'),
    ('ability', 'abilities'),
    ('agency', 'agencies'),
    ('movie', 'movies'),

    ('archive', 'archives'),

    ('index', 'indices'),

    ('wife', 'wives'),
    ('safe', 'saves'),
    ('half', 'halves'),

    ('move', 'moves'),

    ('salesperson', 'salespeople'),
    ('person', 'people'),

    ('spokesman', 'spokesmen'),
    ('man', 'men'),
    ('woman', 'women'),

    ('basis', 'bases'),
    ('diagnosis', 'diagnoses'),
    ('diagnosis_a', 'diagnosis_as'),

    ('datum', 'data'),
    ('medium', 'media'),
    ('stadium', 'stadia'),
    ('analysis', 'analyses'),

    ('node_child', 'node_children'),
    ('child', 'children'),

    ('experience', 'experiences'),
    ('day', 'days'),

    ('comment', 'comments'),
    ('foobar', 'foobars'),
    ('newsletter', 'newsletters'),

    ('old_news', 'old_news'),
    ('news', 'news'),

    ('series', 'series'),
    ('species', 'species'),

    ('quiz', 'quizzes'),

    ('perspective', 'perspectives'),

    ('ox', 'oxen'),
    ('passerby', 'passersby'),
    ('photo', 'photos'),
    ('buffalo', 'buffaloes'),
    ('tomato', 'tomatoes'),
    ('potato', 'potatoes'),
    ('dwarf', 'dwarves'),
    ('elf', 'elves'),
    ('information', 'information'),
    ('equipment', 'equipment'),
    ('bus', 'buses'),
    ('status', 'statuses'),
    ('status_code', 'status_codes'),
    ('mouse', 'mice'),

    ('louse', 'lice'),
    ('house', 'houses'),
    ('octopus', 'octopi'),
    ('virus', 'viri'),
    ('alias', 'aliases'),
    ('portfolio', 'portfolios'),

    ('vertex', 'vertices'),
    ('matrix', 'matrices'),
    ('matrix_fu', 'matrix_fus'),

    ('axis', 'axes'),
    ('testis', 'testes'),
    ('crisis', 'crises'),

    ('rice', 'rice'),
    ('shoe', 'shoes'),

    ('horse', 'horses'),
    ('prize', 'prizes'),
    ('edge', 'edges'),

    ('cow', 'kine'),
    ('database', 'databases'),
    ('human', 'humans'),
)

CAMEL_TO_UNDERSCORE: TestParameters = (
    ('Product',               'product'),
    ('SpecialGuest',          'special_guest'),
    ('ApplicationController', 'application_controller'),
    ('Area51Controller',      'area51_controller'),
)

CAMEL_TO_UNDERSCORE_WITHOUT_REVERSE: TestParameters = (
    ('HTMLTidy',              'html_tidy'),
    ('HTMLTidyGenerator',     'html_tidy_generator'),
    ('FreeBSD',               'free_bsd'),
    ('HTML',                  'html'),
)

STRING_TO_PARAMETERIZED: TestParameters = (
    ('Donald E. Knuth', 'donald-e-knuth'),
    (
        'Random text with *(bad)* characters',
        'random-text-with-bad-characters',
    ),
    ('Allow_Under_Scores', 'allow_under_scores'),
    ('Trailing bad characters!@#', 'trailing-bad-characters'),
    ('!@#Leading bad characters', 'leading-bad-characters'),
    ('Squeeze   separators', 'squeeze-separators'),
    ('Test with + sign', 'test-with-sign'),
    ('Test with malformed utf8 \251', 'test-with-malformed-utf8'),
)

STRING_TO_PARAMETERIZE_WITH_NO_SEPARATOR: TestParameters = (
    ('Donald E. Knuth', 'donaldeknuth'),
    ('With-some-dashes', 'with-some-dashes'),
    ('Random text with *(bad)* characters', 'randomtextwithbadcharacters'),
    ('Trailing bad characters!@#', 'trailingbadcharacters'),
    ('!@#Leading bad characters', 'leadingbadcharacters'),
    ('Squeeze   separators', 'squeezeseparators'),
    ('Test with + sign', 'testwithsign'),
    ('Test with malformed utf8 \251', 'testwithmalformedutf8'),
)

STRING_TO_PARAMETERIZE_WITH_UNDERSCORE: TestParameters = (
    ('Donald E. Knuth', 'donald_e_knuth'),
    (
        'Random text with *(bad)* characters',
        'random_text_with_bad_characters',
    ),
    ('With-some-dashes', 'with-some-dashes'),
    ('Retain_underscore', 'retain_underscore'),
    ('Trailing bad characters!@#', 'trailing_bad_characters'),
    ('!@#Leading bad characters', 'leading_bad_characters'),
    ('Squeeze   separators', 'squeeze_separators'),
    ('Test with + sign', 'test_with_sign'),
    ('Test with malformed utf8 \251', 'test_with_malformed_utf8'),
)

STRING_TO_PARAMETERIZED_AND_NORMALIZED: TestParameters = (
    ('Malmö', 'malmo'),
    ('Garçons', 'garcons'),
    ('Ops\331', 'opsu'),
    ('Ærøskøbing', 'rskbing'),
    ('Aßlar', 'alar'),
    ('Japanese: 日本語', 'japanese'),
)

UNDERSCORE_TO_HUMAN: TestParameters = (
    ('employee_salary',       'Employee salary'),
    ('employee_id',           'Employee'),
    ('underground',           'Underground'),
)

MIXTURE_TO_TITLEIZED: TestParameters = (
    ('active_record',         'Active Record'),
    ('ActiveRecord',          'Active Record'),
    ('action web service',    'Action Web Service'),
    ('Action Web Service',    'Action Web Service'),
    ('Action web service',    'Action Web Service'),
    ('actionwebservice',      'Actionwebservice'),
    ('Actionwebservice',      'Actionwebservice'),
    ("david's code",          "David's Code"),
    ("David's code",          "David's Code"),
    ("david's Code",          "David's Code"),
    ('ana índia',             'Ana Índia'),
    ('Ana Índia',             'Ana Índia'),
)


ORDINAL_NUMBERS: TestParameters = (
    ('-1', '-1st'),
    ('-2', '-2nd'),
    ('-3', '-3rd'),
    ('-4', '-4th'),
    ('-5', '-5th'),
    ('-6', '-6th'),
    ('-7', '-7th'),
    ('-8', '-8th'),
    ('-9', '-9th'),
    ('-10', '-10th'),
    ('-11', '-11th'),
    ('-12', '-12th'),
    ('-13', '-13th'),
    ('-14', '-14th'),
    ('-20', '-20th'),
    ('-21', '-21st'),
    ('-22', '-22nd'),
    ('-23', '-23rd'),
    ('-24', '-24th'),
    ('-100', '-100th'),
    ('-101', '-101st'),
    ('-102', '-102nd'),
    ('-103', '-103rd'),
    ('-104', '-104th'),
    ('-110', '-110th'),
    ('-111', '-111th'),
    ('-112', '-112th'),
    ('-113', '-113th'),
    ('-1000', '-1000th'),
    ('-1001', '-1001st'),
    ('0', '0th'),
    ('1', '1st'),
    ('2', '2nd'),
    ('3', '3rd'),
    ('4', '4th'),
    ('5', '5th'),
    ('6', '6th'),
    ('7', '7th'),
    ('8', '8th'),
    ('9', '9th'),
    ('10', '10th'),
    ('11', '11th'),
    ('12', '12th'),
    ('13', '13th'),
    ('14', '14th'),
    ('20', '20th'),
    ('21', '21st'),
    ('22', '22nd'),
    ('23', '23rd'),
    ('24', '24th'),
    ('100', '100th'),
    ('101', '101st'),
    ('102', '102nd'),
    ('103', '103rd'),
    ('104', '104th'),
    ('110', '110th'),
    ('111', '111th'),
    ('112', '112th'),
    ('113', '113th'),
    ('1000', '1000th'),
    ('1001', '1001st'),
)

UNDERSCORES_TO_DASHES: TestParameters = (
    ('street',                'street'),
    ('street_address',        'street-address'),
    ('person_street_address', 'person-street-address'),
)

STRING_TO_TABLEIZE: TestParameters = (
    ('person', 'people'),
    ('Country', 'countries'),
    ('ChildToy', 'child_toys'),
    ('_RecipeIngredient', '_recipe_ingredients'),
)


def test_pluralize_plurals() -> None:
    assert 'plurals' == inflect.pluralize('plurals')
    assert 'Plurals' == inflect.pluralize('Plurals')


def test_pluralize_empty_string() -> None:
    assert '' == inflect.pluralize('')


@pytest.mark.parametrize(
    ('word',),  # noqa
    [(word,) for word in sorted(inflect._UNCOUNTABLE_WORDS)],
)
def test_uncountability(word: str) -> None:
    assert word == inflect.singularize(word)
    assert word == inflect.pluralize(word)
    assert inflect.pluralize(word) == inflect.singularize(word)


def test_uncountable_word_is_not_greedy() -> None:
    uncountable_word = 'ors'
    countable_word = 'sponsor'

    inflect._UNCOUNTABLE_WORDS.add(uncountable_word)
    inflect._UNCOUNTABLE_PATS.append(inflect._uncountable_pat(uncountable_word))
    try:
        assert uncountable_word == inflect.singularize(uncountable_word)
        assert uncountable_word == inflect.pluralize(uncountable_word)
        assert inflect.pluralize(uncountable_word) == inflect.singularize(uncountable_word)

        assert 'sponsor' == inflect.singularize(countable_word)
        assert 'sponsors' == inflect.pluralize(countable_word)
        assert 'sponsor' == inflect.singularize(inflect.pluralize(countable_word))
    finally:
        inflect._UNCOUNTABLE_WORDS.remove(uncountable_word)
        inflect._UNCOUNTABLE_PATS.pop()


@pytest.mark.parametrize(('singular', 'plural'), SINGULAR_TO_PLURAL)
def test_pluralize_singular(singular: str, plural: str) -> None:
    assert plural == inflect.pluralize(singular)
    assert plural.capitalize() == inflect.pluralize(singular.capitalize())


@pytest.mark.parametrize(('singular', 'plural'), SINGULAR_TO_PLURAL)
def test_singularize_plural(singular: str, plural: str) -> None:
    assert singular == inflect.singularize(plural)
    assert singular.capitalize() == inflect.singularize(plural.capitalize())


@pytest.mark.parametrize(('singular', 'plural'), SINGULAR_TO_PLURAL)
def test_pluralize_plural(singular: str, plural: str) -> None:
    assert plural == inflect.pluralize(plural)
    assert plural.capitalize() == inflect.pluralize(plural.capitalize())


@pytest.mark.parametrize(('before', 'titleized'), MIXTURE_TO_TITLEIZED)
def test_titleize(before: str, titleized: str) -> None:
    assert titleized == inflect.titleize(before)


@pytest.mark.parametrize(('camel', 'underscore'), CAMEL_TO_UNDERSCORE)
def test_camelize(camel: str, underscore: str) -> None:
    assert camel == inflect.camelize(underscore)


def test_camelize_with_lower_downcases_the_first_letter() -> None:
    assert 'capital' == inflect.camelize('Capital', False)


def test_camelize_with_underscores() -> None:
    assert 'CamelCase' == inflect.camelize('Camel_Case')


@pytest.mark.parametrize(
    ('camel', 'underscore'),
    CAMEL_TO_UNDERSCORE + CAMEL_TO_UNDERSCORE_WITHOUT_REVERSE,
)
def test_underscore(camel: str, underscore: str) -> None:
    assert underscore == inflect.underscore(camel)


@pytest.mark.parametrize(
    ('some_string', 'parameterized_string'),
    STRING_TO_PARAMETERIZED,
)
def test_parameterize(some_string: str, parameterized_string: str) -> None:
    assert parameterized_string == inflect.parameterize(some_string)


@pytest.mark.parametrize(
    ('some_string', 'parameterized_string'),
    STRING_TO_PARAMETERIZED_AND_NORMALIZED,
)
def test_parameterize_and_normalize(some_string: str, parameterized_string: str) -> None:
    assert parameterized_string == inflect.parameterize(some_string)


@pytest.mark.parametrize(
    ('some_string', 'parameterized_string'),
    STRING_TO_PARAMETERIZE_WITH_UNDERSCORE,
)
def test_parameterize_with_custom_separator(some_string: str, parameterized_string: str) -> None:
    assert parameterized_string == inflect.parameterize(some_string, '_')


@pytest.mark.parametrize(
    ('some_string', 'parameterized_string'),
    STRING_TO_PARAMETERIZED,
)
def test_parameterize_with_multi_character_separator(
    some_string: str,
    parameterized_string: str,
) -> None:
    assert (
        parameterized_string.replace('-', '__sep__') ==
        inflect.parameterize(some_string, '__sep__')
    )


@pytest.mark.parametrize(
    ('some_string', 'parameterized_string'),
    STRING_TO_PARAMETERIZE_WITH_NO_SEPARATOR,
)
def test_parameterize_with_no_separator(some_string: str, parameterized_string: str) -> None:
    assert parameterized_string == inflect.parameterize(some_string, '')


@pytest.mark.parametrize(('underscore', 'human'), UNDERSCORE_TO_HUMAN)
def test_humanize(underscore: str, human: str) -> None:
    assert human == inflect.humanize(underscore)


@pytest.mark.parametrize(('number', 'ordinalized'), ORDINAL_NUMBERS)
def test_ordinal(number: str, ordinalized: str) -> None:
    assert ordinalized == number + inflect.ordinal(int(number))


@pytest.mark.parametrize(('number', 'ordinalized'), ORDINAL_NUMBERS)
def test_ordinalize(number: str, ordinalized: str) -> None:
    assert ordinalized == inflect.ordinalize(int(number))


@pytest.mark.parametrize(('input', 'expected'), UNDERSCORES_TO_DASHES)
def test_dasherize(input: str, expected: str) -> None:  # noqa
    assert inflect.dasherize(input) == expected


@pytest.mark.parametrize(('string', 'tableized'), STRING_TO_TABLEIZE)
def test_tableize(string: str, tableized: str) -> None:
    assert inflect.tableize(string) == tableized
