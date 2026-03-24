from ..utils import insert_before_first_non_header_line


def test_inserts_before_package_after_line_comment_header() -> None:
    src = """// hello
// world

package com.foo;

class C {}
"""
    out = insert_before_first_non_header_line(src, 'import java.util.*;')

    assert out == """// hello
// world

import java.util.*;
package com.foo;

class C {}
"""


def test_inserts_before_package_after_indented_line_comment_header() -> None:
    src = """   // hello
\t// world

package com.foo;
"""
    out = insert_before_first_non_header_line(src, 'import java.util.*;')

    assert out == """   // hello
\t// world

import java.util.*;
package com.foo;
"""


def test_handles_single_line_block_comment() -> None:
    src = """/* license */
package com.foo;
"""
    out = insert_before_first_non_header_line(src, 'import java.util.*;')

    assert out == """/* license */
import java.util.*;
package com.foo;
"""


def test_handles_multi_line_block_comment() -> None:
    src = """/*
 * license
 * text
 */

package com.foo;

class C {}
"""
    out = insert_before_first_non_header_line(src, 'import java.util.*;')

    assert out == """/*
 * license
 * text
 */

import java.util.*;
package com.foo;

class C {}
"""


def test_handles_indented_block_comment() -> None:
    src = """   /*
    * license
    */
package com.foo;
"""
    out = insert_before_first_non_header_line(src, 'import java.util.*;')

    assert out == """   /*
    * license
    */
import java.util.*;
package com.foo;
"""


def test_handles_mixed_blank_and_comment_header_lines() -> None:
    src = """
// one

/* two
 * three
 */

package com.foo;
"""
    out = insert_before_first_non_header_line(src, '@Generated')

    assert out == """
// one

/* two
 * three
 */

@Generated
package com.foo;
"""


def test_no_header_inserts_at_top() -> None:
    src = """package com.foo;

class C {}
"""
    out = insert_before_first_non_header_line(src, 'import java.util.*;')

    assert out == """import java.util.*;
package com.foo;

class C {}
"""


def test_empty_file() -> None:
    assert insert_before_first_non_header_line('', 'import java.util.*;') == 'import java.util.*;\n'


def test_header_only_file_appends_line() -> None:
    src = """// hello

/* world */
"""
    out = insert_before_first_non_header_line(src, 'import java.util.*;')

    assert out == """// hello

/* world */
import java.util.*;
"""


def test_preserves_crlf_style() -> None:
    src = '// hello\r\n\r\npackage com.foo;\r\n'
    out = insert_before_first_non_header_line(src, 'import java.util.*;')

    assert out == '// hello\r\n\r\nimport java.util.*;\r\npackage com.foo;\r\n'
