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
CFG_INDEXDIR = None
CFG_LOAD = None
CFG_MCP = False
CFG_LANG = None

def usage():
  print("index a folder: ./vaporeon -i [dir] -d [save.db]")
  print("load a db: ./vaporeon -l [save.db] [--mcp]")

if __name__ == "__main__":
  if len(sys.argv) == 1:
    usage()
    sys.exit(0)
  args, opts = getopt.getopt(sys.argv[1:],"d:i:l:",["dir=","index=","load=","mcp","lang="])
  for arg,val in args:
    if arg in ["-i","--index"]:
      CFG_INDEX = val
    elif arg in ["-l","--load"]:
      CFG_LOAD = val
    elif arg in ["-d","--dir"]:
      CFG_INDEXDIR = val
    elif arg == "--mcp":
      CFG_MCP = True
    elif arg == "--lang":
      CFG_LANG = val
  # sanity:
  if CFG_LANG is None:
    print("fatal: you must specify --lang")
    sys.exit(-1)
  if CFG_INDEX is not None and CFG_LOAD is not None:
    print("fatal: you cannot have both -i and -l, choose one")
    sys.exit(-1)
  core.index._set_lang(CFG_LANG)
  if CFG_INDEX is not None:
    core.index.createIndex(CFG_INDEX,CFG_INDEXDIR)
    sys.exit(-1)
  elif CFG_LOAD is not None:
    if CFG_MCP is True:
      core.index._cfg_mcp = True
      core.index._load_index(CFG_LOAD)
      core.mcp.start_mcp()
    else:
      core.index._load_index(CFG_LOAD)
      core.index.run_cli()
