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
"""
A port of Ruby on Rails' inflector to Python.

:copyright: (c) 2012-2020 by Janne Vanhala

:license: MIT, see license above for more details.
"""
import re
import typing as ta
import unicodedata


RegexReplaceList: ta.TypeAlias = list[tuple[str, str]]


##


_PLURALS: RegexReplaceList = [
    (r'(?i)(quiz)$', r'\1zes'),
    (r'(?i)^(oxen)$', r'\1'),
    (r'(?i)^(ox)$', r'\1en'),
    (r'(?i)(m|l)ice$', r'\1ice'),
    (r'(?i)(m|l)ouse$', r'\1ice'),
    (r'(?i)(passer)s?by$', r'\1sby'),
    (r'(?i)(matr|vert|ind)(?:ix|ex)$', r'\1ices'),
    (r'(?i)(x|ch|ss|sh)$', r'\1es'),
    (r'(?i)([^aeiouy]|qu)y$', r'\1ies'),
    (r'(?i)(hive)$', r'\1s'),
    (r'(?i)([lr])f$', r'\1ves'),
    (r'(?i)([^f])fe$', r'\1ves'),
    (r'(?i)sis$', 'ses'),
    (r'(?i)([ti])a$', r'\1a'),
    (r'(?i)([ti])um$', r'\1a'),
    (r'(?i)(buffal|potat|tomat)o$', r'\1oes'),
    (r'(?i)(bu)s$', r'\1ses'),
    (r'(?i)(alias|status)$', r'\1es'),
    (r'(?i)(octop|vir)i$', r'\1i'),
    (r'(?i)(octop|vir)us$', r'\1i'),
    (r'(?i)^(ax|test)is$', r'\1es'),
    (r'(?i)s$', 's'),
    (r'$', 's'),
]

_SINGULARS: RegexReplaceList = [
    (r'(?i)(database)s$', r'\1'),
    (r'(?i)(quiz)zes$', r'\1'),
    (r'(?i)(matr)ices$', r'\1ix'),
    (r'(?i)(vert|ind)ices$', r'\1ex'),
    (r'(?i)(passer)sby$', r'\1by'),
    (r'(?i)^(ox)en', r'\1'),
    (r'(?i)(alias|status)(es)?$', r'\1'),
    (r'(?i)(octop|vir)(us|i)$', r'\1us'),
    (r'(?i)^(a)x[ie]s$', r'\1xis'),
    (r'(?i)(cris|test)(is|es)$', r'\1is'),
    (r'(?i)(shoe)s$', r'\1'),
    (r'(?i)(o)es$', r'\1'),
    (r'(?i)(bus)(es)?$', r'\1'),
    (r'(?i)(m|l)ice$', r'\1ouse'),
    (r'(?i)(x|ch|ss|sh)es$', r'\1'),
    (r'(?i)(m)ovies$', r'\1ovie'),
    (r'(?i)(s)eries$', r'\1eries'),
    (r'(?i)([^aeiouy]|qu)ies$', r'\1y'),
    (r'(?i)([lr])ves$', r'\1f'),
    (r'(?i)(tive)s$', r'\1'),
    (r'(?i)(hive)s$', r'\1'),
    (r'(?i)([^f])ves$', r'\1fe'),
    (r'(?i)(t)he(sis|ses)$', r'\1hesis'),
    (r'(?i)(s)ynop(sis|ses)$', r'\1ynopsis'),
    (r'(?i)(p)rogno(sis|ses)$', r'\1rognosis'),
    (r'(?i)(p)arenthe(sis|ses)$', r'\1arenthesis'),
    (r'(?i)(d)iagno(sis|ses)$', r'\1iagnosis'),
    (r'(?i)(b)a(sis|ses)$', r'\1asis'),
    (r'(?i)(a)naly(sis|ses)$', r'\1nalysis'),
    (r'(?i)([ti])a$', r'\1um'),
    (r'(?i)(n)ews$', r'\1ews'),
    (r'(?i)(ss)$', r'\1'),
    (r'(?i)s$', ''),
]

_UNCOUNTABLES: set[str] = {
    'equipment',
    'fish',
    'information',
    'jeans',
    'money',
    'rice',
    'series',
    'sheep',
    'species'}


def _irregular(singular: str, plural: str) -> None:
    """A convenience function to add appropriate rules to plurals and singular for irregular words."""

    def caseinsensitive(string: str) -> str:
        return ''.join('[' + char + char.upper() + ']' for char in string)

    if singular[0].upper() == plural[0].upper():
        _PLURALS.insert(0, (
            fr'(?i)({singular[0]}){singular[1:]}$',
            r'\1' + plural[1:],
        ))
        _PLURALS.insert(0, (
            fr'(?i)({plural[0]}){plural[1:]}$',
            r'\1' + plural[1:],
        ))
        _SINGULARS.insert(0, (
            fr'(?i)({plural[0]}){plural[1:]}$',
            r'\1' + singular[1:],
        ))

    else:
        _PLURALS.insert(0, (
            fr'{singular[0].upper()}{caseinsensitive(singular[1:])}$',
            plural[0].upper() + plural[1:],
        ))
        _PLURALS.insert(0, (
            fr'{singular[0].lower()}{caseinsensitive(singular[1:])}$',
            plural[0].lower() + plural[1:],
        ))
        _PLURALS.insert(0, (
            fr'{plural[0].upper()}{caseinsensitive(plural[1:])}$',
            plural[0].upper() + plural[1:],
        ))
        _PLURALS.insert(0, (
            fr'{plural[0].lower()}{caseinsensitive(plural[1:])}$',
            plural[0].lower() + plural[1:],
        ))
        _SINGULARS.insert(0, (
            fr'{plural[0].upper()}{caseinsensitive(plural[1:])}$',
            singular[0].upper() + singular[1:],
        ))
        _SINGULARS.insert(0, (
            fr'{plural[0].lower()}{caseinsensitive(plural[1:])}$',
            singular[0].lower() + singular[1:],
        ))


_irregular('person', 'people')
_irregular('man', 'men')
_irregular('human', 'humans')
_irregular('child', 'children')
_irregular('sex', 'sexes')
_irregular('move', 'moves')
_irregular('cow', 'kine')
_irregular('zombie', 'zombies')


##


def camelize(string: str, uppercase_first_letter: bool = True) -> str:
    """Convert strings to CamelCase."""

    if uppercase_first_letter:
        return re.sub(r'(?:^|_)(.)', lambda m: m.group(1).upper(), string)
    else:
        return string[0].lower() + camelize(string)[1:]


def dasherize(word: str) -> str:
    """Replace underscores with dashes in the string."""

    return word.replace('_', '-')


def humanize(word: str) -> str:
    """
    Capitalize the first word and turn underscores into spaces and strip a trailing ``"_id"``, if any. Like
    :func:`titleize`, this is meant for creating pretty output.
    """

    word = re.sub(r'_id$', '', word)
    word = word.replace('_', ' ')
    word = re.sub(r'(?i)([a-z\d]*)', lambda m: m.group(1).lower(), word)
    word = re.sub(r'^\w', lambda m: m.group(0).upper(), word)
    return word


def ordinal(number: int) -> str:
    """
    Return the suffix that should be added to a number to denote the position in an ordered sequence such as 1st, 2nd,
    3rd, 4th.
    """

    number = abs(int(number))
    if number % 100 in (11, 12, 13):
        return 'th'
    else:
        return {
            1: 'st',
            2: 'nd',
            3: 'rd',
        }.get(number % 10, 'th')


def ordinalize(number: int) -> str:
    """
    Turn a number into an ordinal string used to denote the position in an ordered sequence such as 1st, 2nd, 3rd, 4th.
    """

    return f'{number}{ordinal(number)}'


def parameterize(string: str, separator: str = '-') -> str:
    """Replace special characters in a string so that it may be used as part of a 'pretty' URL."""

    string = transliterate(string)
    # Turn unwanted chars into the separator
    string = re.sub(r'(?i)[^a-z0-9\-_]+', separator, string)
    if separator:
        re_sep = re.escape(separator)
        # No more than one of the separator in a row.
        string = re.sub(fr'{re_sep}{{2,}}', separator, string)
        # Remove leading/trailing separator.
        string = re.sub(fr'(?i)^{re_sep}|{re_sep}$', '', string)

    return string.lower()


def pluralize(word: str) -> str:
    """Return the plural form of a word."""

    if not word or word.lower() in _UNCOUNTABLES:
        return word
    else:
        for rule, replacement in _PLURALS:
            if re.search(rule, word):
                return re.sub(rule, replacement, word)
        return word


def singularize(word: str) -> str:
    """Return the singular form of a word, the reverse of :func:`pluralize`."""

    for inflection in _UNCOUNTABLES:
        if re.search(fr'(?i)\b({inflection})\Z', word):
            return word

    for rule, replacement in _SINGULARS:
        if re.search(rule, word):
            return re.sub(rule, replacement, word)
    return word


def tableize(word: str) -> str:
    """
    Create the name of a table like Rails does for models to table names. This method uses the :func:`pluralize` method
    on the last word in the string.
    """

    return pluralize(underscore(word))


def titleize(word: str) -> str:
    """
    Capitalize all the words and replace some characters in the string to create a nicer looking title. :func:`titleize`
    is meant for creating pretty output.
    """

    return re.sub(
        r"\b('?\w)",
        lambda match: match.group(1).capitalize(),
        humanize(underscore(word)).title(),
    )


def transliterate(string: str) -> str:
    """
    Replace non-ASCII characters with an ASCII approximation. If no approximation exists, the non-ASCII character is
    ignored. The string must be ``unicode``.
    """

    normalized = unicodedata.normalize('NFKD', string)
    return normalized.encode('ascii', 'ignore').decode('ascii')


def underscore(word: str) -> str:
    """Make an underscored, lowercase form from the expression in the string."""

    word = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', word)
    word = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', word)
    word = word.replace('-', '_')
    return word.lower()
