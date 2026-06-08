# vaporeon

![its vaporeon!](docs/img/vaporeon.png)

Docs: [database](docs/DB.md)

Vaporeon is a simple tree-sitter based Python app, which reads through a directory of C code and attempts to create a call database (of which functions call which other functions). To use this, start by indexing a folder of source code (c, cpp, ts and tsx are support for --lang):

```
./vaporeon.py --lang c -i ~/data/qemu -d ~/data/qemu_src.db"
```

Now, you can access the database and attempt to map "hot paths" through a codebase:

```
./vaporeon.py --lang c -l ~/data/qemu_src.db
 > .xrefs_from transaction_action
info: called .xrefs_from('transaction_action')
(446, 59, 'transaction_action', 'external_snapshot_action')
(447, 59, 'transaction_action', 'drive_backup_action')
(448, 59, 'transaction_action', 'blockdev_backup_action')
(449, 59, 'transaction_action', 'abort_action')
(450, 59, 'transaction_action', 'internal_snapshot_action')
(451, 59, 'transaction_action', 'block_dirty_bitmap_add_action')
(452, 59, 'transaction_action', 'block_dirty_bitmap_clear_action')
(453, 59, 'transaction_action', 'block_dirty_bitmap_enable_action')
(454, 59, 'transaction_action', 'block_dirty_bitmap_disable_action')
(455, 59, 'transaction_action', 'block_dirty_bitmap_merge_action')
(456, 59, 'transaction_action', 'block_dirty_bitmap_remove_action')
(457, 59, 'transaction_action', 'g_assert_not_reached')
```

Similarly, .paths_to and .paths_from can analyze call paths to and from a given function. This aims to answer, "can I start at X function and touch Y function"

This identifies all (single-depth) calls made from transaction_action.

It is not perfect by a long shot - but right now, we do not care, because it is better than having AI stumble through files with ripgrep and glob.

You probably shouldn't be here, you probably want /r/vibecoding instead.
