# vaporeon

![its vaporeon!](docs/img/vaporeon.png)

Docs: [database](docs/DB.md)

Vaporeon is a simple tree-sitter based Python app, which reads through a directory of C code and attempts to create a call database (of which functions call which other functions). To use this, start by indexing a folder of source code (c, cpp, ts and tsx are support for --lang):

```
./vaporeon -lang ts -i /var/tmp/portkey -d /var/tmp/portkey.db"
```

Now, you can access the database and attempt to trace code through the database:

```
./vaporeon.py --lang ts -d /var/tmp/portkey.db
.select from functions where name like '%pii%'
(51, 'maskPiiEntries', '/var/tmp/portkey/plugins/promptfoo/pii.ts', 287, 582)
(53, 'redactPii', '/var/tmp/portkey/plugins/promptfoo/pii.ts', 610, 1261)
(75, 'detectPII', '/var/tmp/portkey/plugins/portkey/pii.ts', 303, 1065)
(159, 'redactPii', '/var/tmp/portkey/plugins/patronus/pii.ts', 1205, 2065)
(735, 'redactPii', '/var/tmp/portkey/plugins/bedrock/util.ts', 2557, 3845)
(781, 'getPIIParameters', '/var/tmp/portkey/plugins/acuvity/scan.test.ts', 1063, 1290)
(782, 'getPIIRedactParameters', '/var/tmp/portkey/plugins/acuvity/scan.test.ts', 1299, 1531)
.xrefs_to getPIIParameters
(8446, 786, 'getParameters', 'getPIIParameters')
(8607, 787, '<anonymous>', 'getPIIParameters')
(8779, 799, '<anonymous>', 'getPIIParameters')
.src getPIIParameters
function getPIIParameters(): PluginParameters {
  return {
    pii: true,
    pii_redact: false,
    pii_categories: [
      'email_address',
      'ssn',
      'person',
      'credit_card',
      'phone_number',
    ],
  };
}
```

Similarly, .paths_to and .paths_from can analyze call paths to and from a given function. This aims to answer, "can I start at X function and touch Y function". This is still a work in progress, and has tons of dumb corner cases. This isn't taint-tracking by any means.

It is not perfect by a long shot - but right now, we do not care, because it is better than having AI stumble through files with ripgrep and glob.

You probably shouldn't be here, you probably want /r/vibecoding instead.
