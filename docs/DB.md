# vaporeon - database

The vaporeon database is laid out as follows:

```
CREATE TABLE IF NOT EXISTS functions(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  file TEXT NOT NULL,
  start INTEGER NOT NULL,
  end INTEGER NOT NULL
)

CREATE TABLE IF NOT EXISTS calls(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  srcid INTEGER NOT NULL,
  src TEXT NOT NULL,
  dest TEXT NOT NULL
)
```

The functions table allows us to fetch functions from source code (by specifying filename, begin and end bytes). The calls table links source functions (via functions.id) to destinations (text: because not everything has an id, and because we must handle the case of names overlapping)
