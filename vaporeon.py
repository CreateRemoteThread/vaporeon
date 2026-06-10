#!/usr/bin/env python3

import readline
import getopt
import glob
import os
import sys
import sqlite3
# import core
import core.mcp
import core.index

CFG_INDEX = None
CFG_INDEXDB = None
CFG_MCP = False
CFG_LANG = None

def usage():
  print("index a folder: ./vaporeon -i [dir] -d [save.db]")
  print("load a db: ./vaporeon -d [save.db] [--mcp]")

if __name__ == "__main__":
  if len(sys.argv) == 1:
    usage()
    sys.exit(0)
  args, opts = getopt.getopt(sys.argv[1:],"d:i:l:",["db=","index=","load=","mcp","lang="])
  for arg,val in args:
    if arg in ["-i","--index"]:
      CFG_INDEX = os.path.expanduser(val)
    elif arg in ["-d","--db"]:
      CFG_INDEXDB = os.path.expanduser(val)
    elif arg == "--mcp":
      CFG_MCP = True
    elif arg == "--lang":
      CFG_LANG = val
  # sanity:
  if CFG_LANG is None:
    print("fatal: you must specify --lang")
    sys.exit(-1)
  core.index._set_lang(CFG_LANG)
  if CFG_INDEX is not None:
    core.index.createIndex(CFG_INDEX,CFG_INDEXDB)
    sys.exit(-1)
  elif CFG_INDEXDB is not None:
    if CFG_MCP is True:
      core.index._cfg_mcp = True
      core.index._load_index(CFG_INDEXDB)
      core.mcp.start_mcp()
    else:
      core.index._load_index(CFG_INDEXDB)
      core.index.run_cli()
  else:
    print("fatal: you must specify -d [filename.db]")
