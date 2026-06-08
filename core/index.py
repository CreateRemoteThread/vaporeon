#!/usr/bin/env python3

import sqlite3
import sys
from typing import Annotated
from tree_sitter import Language, Parser
import glob
import os

_cfg_mcp = False

def __internal_print(str):
  global _cfg_mcp  
  if _cfg_mcp:
    pass
  else:
    print(str)

conn = None
cur = None
fs_ext = []

_extract_functions = None

def _set_lang(lang):
  global parser, fs_ext, _extract_functions
  parser = Parser()
  if lang == "c":
    import tree_sitter_c
    parser.language = Language(tree_sitter_c.language())
    fs_ext = ["*.c","*.h"]
    import core.lang_c
    _extract_functions = core.lang_c._extract_functions
  elif lang == "cpp":
    import tree_sitter_cpp
    parser.language = Language(tree_sitter_cpp.language())
    fs_ext = ["*.c","*.h","*.cpp","*.hpp"]
  elif lang == "tsx":
    import tree_sitter_typescript
    parser.language = Language(tree_sitter_typescript.language_tsx())
    fs_ext = ["*.tsx"]
    import core.lang_ts
    _extract_functions = core.lang_ts._extract_functions
  elif lang == "ts":
    import tree_sitter_typescript
    parser.language = Language(tree_sitter_typescript.language_typescript())
    fs_ext = ["*.ts"]
    import core.lang_ts
    _extract_functions = core.lang_ts._extract_functions

def paths_from(fn: Annotated[str, "Function to get paths from"]):
  paths = []  
  def _path_from(fn,callpath,max_depth):
    data = xrefs_from(fn)
    if len(data) == 0 or max_depth == 0:
      paths.append("->".join(callpath + [fn]))
    else:
      children = []
      for (id,srcid,src,dest) in data:
        children.append(dest)
      for c in children:
        if c in callpath or c == fn:
          continue
        _path_from(c,callpath + [fn],max_depth - 1)
  _path_from(fn,[],10)
  __internal_print(paths)
  return paths
  # return x

def paths_to(fn: Annotated[str, "Function to get paths to"]):
  paths = []  
  def _path_to(fn,callpath,max_depth):
    data = xrefs_to(fn)
    if len(data) == 0 or max_depth == 0:
      paths.append("->".join([fn] + callpath))
    else:
      children = []
      for (id,srcid,src,dest) in data:
        children.append(dest)
      for c in children:
        if c in callpath or c == fn:
          continue
        _path_to(c,[fn] + callpath,max_depth - 1)
  _path_to(fn,[],10)
  __internal_print(paths)
  return paths
  # return x

def _load_index(filename):
  global conn, cur
  conn = sqlite3.connect(filename)
  cur = conn.cursor()

def xrefs_from(fn: Annotated[str, "Function to get xrefs from"]):
  global cur
  cur.execute("select * from calls where src = ?",(fn,))
  rows = cur.fetchall()
  for row in rows:
    __internal_print(row)
  return rows
xrefs_from.__doc__ = "Find what a function calls."

def xrefs_to(fn: Annotated[str, "Function to get xrefs to"]):
  global cur
  cur.execute("select * from calls where dest = ?",(fn,))
  rows = cur.fetchall()
  for row in rows:
    __internal_print(row)
  return rows
xrefs_to.__doc__ = "Find what calls a function."

def createIndex(index_dir,index_db):
  global fs_ext, parser
  __internal_print("info: calling createIndex('%s','%s')" % (index_dir,index_db))
  if index_db is None:
    __internal_print("fatal: supply a db filename with -d")
    sys.exit(-1)
  files = []
  for ext in fs_ext:
    files += [ f for f in glob.glob(index_dir + "/**/" + ext,recursive=True) if os.path.isfile(f)]
  conn = sqlite3.connect(index_db)
  cur = conn.cursor()
  cur.execute("CREATE TABLE IF NOT EXISTS functions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, file TEXT NOT NULL, start INTEGER NOT NULL, end INTEGER NOT NULL)")
  cur.execute("CREATE TABLE IF NOT EXISTS calls (id INTEGER PRIMARY KEY AUTOINCREMENT, srcid INTEGER NOT NULL, src TEXT NOT NULL, dest TEXT NOT NULL)")
  max_count = len(files)
  i = 1
  for f in files:
    __internal_print("info: analyzing '%s' [%d/%d]" % (f,i,max_count))
    i += 1
    with open(f,"rb") as fp:
      _extract_functions(f,fp.read(),db=cur,parser=parser)
  conn.commit()
  conn.close() 

def get_src(fn_name):
  global cur
  fn_name_int = 0
  try:
    fn_name_int = int(fn_name)
  except:
    pass
  if fn_name_int != 0:
    cur.execute("select * from functions where id = ?",(fn_name_int,))
  else:
    cur.execute("select * from functions where name = ?",(fn_name,))
  rows = cur.fetchall()
  if len(rows) == 0:
    __internal_print("error: fn not found")
    return None  
  for (id,name,file,start,end) in rows:
    with open(file,"rb") as f:
      fn_src = f.read()[start:end]
    __internal_print(fn_src.decode("utf-8"))
    
def run_cli():
  while True:
    in_cmd = input(" > ").strip()
    if in_cmd.startswith(".select"):
      __internal_print("info: pass directly to sqlite3")
      cur.execute(in_cmd[1:])
      if cur.description is not None:
        rows = cur.fetchall()
        for row in rows:
          __internal_print(row)
      else:
        __internal_print("error: no result")
      continue
    tokens = in_cmd.split()
    if tokens[0] == ".quit":
      __internal_print("bye!")
      sys.exit(0)
    elif tokens[0] == ".xrefs_to" and len(tokens) == 2:
      __internal_print("info: called .path_to('%s')" % tokens[1])
      xrefs_to(tokens[1])
    elif tokens[0] == ".xrefs_from" and len(tokens) == 2:
      __internal_print("info: called .xrefs_from('%s')" % tokens[1])
      xrefs_from(tokens[1])
    elif tokens[0] == ".paths_from" and len(tokens) == 2:
      __internal_print("info: called .paths_from('%s')" % tokens[1])
      paths_from(tokens[1])
    elif tokens[0] == ".paths_to" and len(tokens) == 2:
      __internal_print("info: called .paths_to('%s')" % tokens[1])
      paths_to(tokens[1])
    elif tokens[0] == ".src" and len(tokens) == 2:
      __internal_print("info: called .src('%s')" % tokens[1])
      get_src(tokens[1])
