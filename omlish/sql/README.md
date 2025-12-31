# Overview

SQL utilities including a dbapi abstraction, query builder, and table definition system. Designed as a lightweight
alternative to SQLAlchemy for cases where full ORM features aren't needed.

# Key Components

- **[api](https://github.com/wrmsr/omlish/blob/master/omlish/sql/api)** - Database API abstraction over dbapi-compatible
  drivers:
  - Unified interface across different SQL databases.
  - Connection pooling and transaction management.
  - SQLAlchemy adapter for interoperability.
- **[queries](https://github.com/wrmsr/omlish/blob/master/omlish/sql/queries)** - SQL query builder with fluent
  interface:
  - Type-safe query construction.
  - Select, insert, update, delete operations.
  - Joins, where clauses, ordering, limits.
- **[tabledefs](https://github.com/wrmsr/omlish/blob/master/omlish/sql/tabledefs)** - Table definition system for
  schema management.
- **[parsing](https://github.com/wrmsr/omlish/blob/master/omlish/sql/parsing)** - SQL parsing utilities.
- **[dbapi](https://github.com/wrmsr/omlish/blob/master/omlish/sql/dbapi)** - Dbapi (PEP 249) integration and
  utilities.
- **[alchemy](https://github.com/wrmsr/omlish/blob/master/omlish/sql/alchemy)** - SQLAlchemy integration (optional
  dependency).

# Key Features

- **Database abstraction** - Write database-agnostic code that works across PostgreSQL, MySQL, SQLite, etc.
- **Query builder** - Construct SQL queries programmatically with type safety.
- **Connection management** - Handle connection lifecycle, pooling, and transactions.
- **SQLAlchemy interop** - Adapt the internal API to work with SQLAlchemy when needed.
- **Lightweight** - Minimal dependencies, no full ORM overhead.

# Notable Modules

- **[api/engines](https://github.com/wrmsr/omlish/blob/master/omlish/sql/api/engines.py)** - Database engine
  abstraction.
- **[api/connections](https://github.com/wrmsr/omlish/blob/master/omlish/sql/api/connections.py)** - Connection
  management.
- **[queries/builder](https://github.com/wrmsr/omlish/blob/master/omlish/sql/queries)** - Query builder API.
- **[dbapi/drivers](https://github.com/wrmsr/omlish/blob/master/omlish/sql/dbapi)** - Dbapi driver support.
- **[alchemy/adapter](https://github.com/wrmsr/omlish/blob/master/omlish/sql/alchemy)** - SQLAlchemy adapter.
- **[dbs](https://github.com/wrmsr/omlish/blob/master/omlish/sql/dbs.py)** - Database utilities.
- **[params](https://github.com/wrmsr/omlish/blob/master/omlish/sql/params.py)** - Parameter handling.
- **[qualifiedname](https://github.com/wrmsr/omlish/blob/master/omlish/sql/qualifiedname.py)** - Qualified name
  handling (schema.table.column).

# Example Usage

```python
from omlish.sql import api

# Connect to database
engine = api.create_engine('postgresql://user:pass@localhost/db')
conn = engine.connect()

# Execute query
result = conn.execute('SELECT * FROM users WHERE id = ?', [user_id])
for row in result:
    print(row)

# Query builder
from omlish.sql import queries as q
query = (
    q.select('users')
    .where(q.eq('id', user_id))
    .order_by('created_at', desc=True)
    .limit(10)
)
result = conn.execute(query)
```

# Design Philosophy

SQL utilities should:
- **Be lightweight** - Provide essential features without ORM complexity.
- **Be portable** - Abstract database differences where reasonable.
- **Be composable** - Build queries programmatically piece by piece.
- **Be explicit** - Don't hide SQL behind too much magic.

This package has moved away from SQLAlchemy to a custom internal API, but retains SQLAlchemy as an optional dependency
for interoperability via adapters.

# Migration from SQLAlchemy

The codebase has migrated from SQLAlchemy to the internal SQL API for:
- **Simplicity** - Avoid SQLAlchemy's complexity for non-ORM use cases.
- **Control** - Full control over query generation and execution.
- **Dependencies** - Reduce dependency footprint.

SQLAlchemy support remains via the `alchemy` adapter for cases where interop is needed.
