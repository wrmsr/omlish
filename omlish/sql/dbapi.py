"""
https://peps.python.org/pep-0249/

==

apilevel = '2.0'

threadsafety:
 0 - Threads may not share the module.
 1 - Threads may share the module, but not connections.
 2 - Threads may share the module and connections.
 3 - Threads may share the module, connections and cursors.

paramstyle:
 qmark - Question mark style, e.g. ...WHERE name=?
 numeric - Numeric, positional style, e.g. ...WHERE name=:1
 named - Named style, e.g. ...WHERE name=:name
 format - ANSI C printf format codes, e.g. ...WHERE name=%s
 pyformat - Python extended format codes, e.g. ...WHERE name=%(name)s

Exception
| Warning
| Error
 | InterfaceError
 | DatabaseError
  | DataError
  | OperationalError
  | IntegrityError
  | InternalError
  | ProgrammingError
  | NotSupportedError

Date(year, month, day)
Time(hour, minute, second)
Timestamp(year, month, day, hour, minute, second)
DateFromTicks(ticks)
TimeFromTicks(ticks)
TimestampFromTicks(ticks)
Binary(string)

STRING type
BINARY type
NUMBER type
DATETIME type
ROWID type
"""
