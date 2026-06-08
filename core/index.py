#!/usr/bin/env python3

import sqlite3
import sys
from typing import Annotated
from tree_sitter import Language, Parser
import glob
import os

conn = None
cur = None
fs_ext = []

def _set_lang(lang):
  global parser, fs_ext
  parser = Parser()
  if lang == "c":
    import tree_sitter_c
    parser.language = Language(tree_sitter_c.language())
    fs_ext = ["*.c","*.h"]
  elif lang == "cpp":
    import tree_sitter_cpp
    parser.language = Language(tree_sitter_cpp.language())
    fs_ext = ["*.c","*.h","*.cpp","*.hpp"]
  elif lang == "tsx":
    import tree_sitter_typescript
    parser.language = Language(tree_sitter_typescript.language_tsx())
    fs_ext = ["*.tsx"]
  elif lang == "ts":
    import tree_sitter_typescript
    parser.language = Language(tree_sitter_typescript.language_typescript())
    fs_ext = ["*.ts"]

def _get_node_text(node,c_src):
  return c_src[node.start_byte:node.end_byte]

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
  print(paths)
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
  print(paths)
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

def _extract_calls(fn,c_src,parent,parent_name,db):
  tree = parser.parse(c_src)
  # calls = []
  def visit(node):
    if node.type == "call_expression":
      function_node = node.child_by_field_name("function")
      arguments_node = node.child_by_field_name("arguments")
      if function_node:
        fn_dest = _get_node_text(function_node,c_src).decode("utf-8").strip()
      else:
        fn_dest = "<unknown>"
      db.execute("INSERT INTO calls (srcid,src, dest) VALUES (?,?,?)",(parent,parent_name,fn_dest))
      # calls.append({
      #   "name":_get_node_text(function_node,c_src) if function_node else None,
      #   "expression":_get_node_text(node,c_src)
      # })
    for child in node.children:
      visit(child)
  visit(tree.root_node)
  # return calls

def _extract_functions(fn,c_src,db):
  tree = parser.parse(c_src)
  functions = []
  def visit(node):
    if node.type == "function_definition":
      declarator = node.child_by_field_name("declarator")
      function_name = None
      # Walk down nested declarators to find the identifier
      def find_identifier(n):
        if n.type == "identifier":
          return _get_node_text(n, c_src)
        for child in n.children:
          result = find_identifier(child)
          if result:
            return result
        return None
      if declarator:
        function_name = find_identifier(declarator)
      if function_name is None:
        function_name = "<unknown>"
      else:
        function_name = function_name.decode("utf-8").strip()
      node_text = _get_node_text(node,c_src)
      db.execute("INSERT INTO functions (name,file,start,end) VALUES (?,?,?,?)",(function_name,fn,node.start_byte, node.end_byte))
      # functions.append({
      #   "name": function_name,
      #   "start_line": node.start_point[0] + 1,
      #   "end_line": node.end_point[0] + 1,
      #   "source": node_text,
      # })
      _extract_calls(fn,node_text,parent=db.lastrowid,parent_name=function_name,db=db)
      # print(_extract_calls(_get_node_text(node, c_src)))
    for child in node.children:
      visit(child)
  visit(tree.root_node)

def createIndex(index_dir,index_db):
  global fs_ext
  print("info: calling createIndex('%s','%s')" % (index_dir,index_db))
  if index_db is None:
    print("fatal: supply a db filename with -d")
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
    print("info: analyzing '%s' [%d/%d]" % (f,i,max_count))
    i += 1
    with open(f,"rb") as fp:
      _extract_functions(f,fp.read(),db=cur)
  conn.commit()
  conn.close() 

def run_cli():
  while True:
    in_cmd = input(" > ").strip()
    if in_cmd.startswith(".select"):
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
