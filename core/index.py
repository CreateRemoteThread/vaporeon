#!/usr/bin/env python3

import sqlite3
import sys
from typing import Annotated

conn = None
cur = None

def paths_to(fn: Annotated[str, "Function to get paths to"]):
  x = _path_to(fn,[],10)
  print(x)
  return x

def _path_to(fn,callpath,max_depth):
  data = xrefs_to(fn)
  if len(data) == 0 or max_depth == 0:
    return [fn] + callpath
  else:
    children = []
    for (id,srcid,src,dest) in data:
      children.append(dest)
    return [_path_from(kid,[fn] + callpath,max_depth - 1) for kid in children]
  

def paths_from(fn: Annotated[str, "Function to get paths from"]):
  x = _path_from(fn,[],10)
  print(x)
  return x

def _path_from(fn,callpath,max_depth):
  data = xrefs_from(fn)
  if len(data) == 0 or max_depth == 0:
    return callpath + [fn]
  else:
    children = []
    for (id,srcid,src,dest) in data:
      children.append(dest)
    return [_path_from(kid,callpath + [fn],max_depth - 1) for kid in children]

def _load_index(filename):
  global conn, cur
  conn = sqlite3.connect(filename)
  cur = conn.cursor()

def xrefs_from(fn: Annotated[str, "Function to get xrefs from"]):
  global cur
  cur.execute("select * from calls where src = ?",(fn,))
  rows = cur.fetchall()
  for row in rows:
    print(row)
  return rows
xrefs_from.__doc__ = "Find what a function calls."

def xrefs_to(fn: Annotated[str, "Function to get xrefs to"]):
  global cur
  cur.execute("select * from calls where dest = ?",(fn,))
  rows = cur.fetchall()
  for row in rows:
    print(row)
  return rows
xrefs_to.__doc__ = "Find what calls a function."

def run_cli():
  while True:
    in_cmd = input(" > ").strip()
    if in_cmd.startswith("!"):
      print("info: pass directly to sqlite3")
      cur.execute(in_cmd[1:])
      if cur.description is not None:
        rows = cur.fetchall()
        for row in rows:
          print(row)
      else:
        print("error: no result")
      continue
    tokens = in_cmd.split()
    if tokens[0] == ".quit":
      print("bye!")
      sys.exit(0)
    elif tokens[0] == ".xrefs_to" and len(tokens) == 2:
      print("info: called .path_to('%s')" % tokens[1])
      xrefs_to(tokens[1])
    elif tokens[0] == ".xrefs_from" and len(tokens) == 2:
      print("info: called .xrefs_from('%s')" % tokens[1])
      xrefs_from(tokens[1])
    elif tokens[0] == ".paths_from" and len(tokens) == 2:
      print("info: called .paths_from('%s')" % tokens[1])
      paths_from(tokens[1])
    elif tokens[0] == ".paths_to" and len(tokens) == 2:
      print("info: called .paths_to('%s')" % tokens[1])
      paths_to(tokens[1])
