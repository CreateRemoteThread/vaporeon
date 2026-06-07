#!/usr/bin/env python3

import getopt
from tree_sitter import Language, Parser
import tree_sitter_c as tsc
import glob
import os
import sys
import sqlite3
import core
import core.mcp
import core.index

CFG_INDEX = None
CFG_INDEXDIR = None
CFG_LOAD = None
CFG_MCP = False

def usage():
  print("index a folder: ./vaporeon -i [dir] -d [save.db]")
  print("load a db: ./vaporeon -l [save.db] [--mcp]")

if __name__ == "__main__":
  if len(sys.argv) == 1:
    usage()
    sys.exit(0)
  args, opts = getopt.getopt(sys.argv[1:],"d:i:l:",["dir=","index=","load=","mcp"])
  for arg,val in args:
    if arg in ["-i","--index"]:
      CFG_INDEX = val
    elif arg in ["-l","--load"]:
      CFG_LOAD = val
    elif arg in ["-d","--dir"]:
      CFG_INDEXDIR = val
    elif arg == "--mcp":
      CFG_MCP = True
  # sanity:
  if CFG_INDEX is not None and CFG_LOAD is not None:
    print("fatal: you cannot have both -i and -l, choose one")
    sys.exit(0)
  elif CFG_INDEX is not None:
    core.createIndex(CFG_INDEX,CFG_INDEXDIR)
    sys.exit(0)
  elif CFG_LOAD is not None:
    if CFG_MCP is True:
      core.index._load_index(CFG_LOAD)
      core.mcp.start_mcp()
    else:
      core.index._load_index(CFG_LOAD)
      # core.loadIndex(CFG_LOAD)
