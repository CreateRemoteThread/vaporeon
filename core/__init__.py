#!/usr/bin/env python3

import sqlite3
import os
import glob
import sys
from tree_sitter import Language, Parser
import tree_sitter_c as tsc

parser = Parser()
parser.language = Language(tsc.language())

def get_node_text(node,c_src):
  return c_src[node.start_byte:node.end_byte]

def extract_calls(fn,c_src,parent,db):
  tree = parser.parse(c_src)
  # calls = []
  def visit(node):
    if node.type == "call_expression":
      function_node = node.child_by_field_name("function")
      arguments_node = node.child_by_field_name("arguments")
      db.execute("INSERT INTO calls (src, dest) VALUES (?,?)",(parent,get_node_text(function_node,c_src) if function_node else "<unknown>"))
      # calls.append({
      #   "name":get_node_text(function_node,c_src) if function_node else None,
      #   "expression":get_node_text(node,c_src)
      # })
    for child in node.children:
      visit(child)
  visit(tree.root_node)
  # return calls

def extract_functions(fn,c_src,db):
  tree = parser.parse(c_src)
  functions = []
  def visit(node):
    if node.type == "function_definition":
      declarator = node.child_by_field_name("declarator")
      function_name = None
      # Walk down nested declarators to find the identifier
      def find_identifier(n):
        if n.type == "identifier":
          return get_node_text(n, c_src)
        for child in n.children:
          result = find_identifier(child)
          if result:
            return result
        return None
      if declarator:
        function_name = find_identifier(declarator)
      if function_name is None:
        function_name = "<unknown>"
      node_text = get_node_text(node,c_src)
      db.execute("INSERT INTO functions (name,file,start,end) VALUES (?,?,?,?)",(function_name,fn,node.start_byte, node.end_byte))
      # functions.append({
      #   "name": function_name,
      #   "start_line": node.start_point[0] + 1,
      #   "end_line": node.end_point[0] + 1,
      #   "source": node_text,
      # })
      extract_calls(fn,node_text,parent=db.lastrowid,db=db)
      # print(extract_calls(get_node_text(node, c_src)))
    for child in node.children:
      visit(child)
  visit(tree.root_node)

def createIndex(index_dir,index_db):
  print("info: calling createIndex('%s','%s')" % (index_dir,index_db))
  if index_db is None:
    print("fatal: supply a db filename with -d")
    sys.exit(-1)
  files = glob.glob(index_dir + "/**/*.c",recursive=True) + glob.glob(index_dir + "/**/*.h",recursive=True)
  conn = sqlite3.connect(index_db)
  cur = conn.cursor()
  cur.execute("CREATE TABLE IF NOT EXISTS functions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, file TEXT NOT NULL, start INTEGER NOT NULL, end INTEGER NOT NULL)")
  cur.execute("CREATE TABLE IF NOT EXISTS calls (id INTEGER PRIMARY KEY AUTOINCREMENT, src INTEGER NOT NULL, dest TEXT NOT NULL)")
  max_count = len(files)
  i = 1
  for f in files:
    print("info: analyzing '%s' [%d/%d]" % (f,i,max_count))
    i += 1
    with open(f,"rb") as fp:
      extract_functions(f,fp.read(),db=cur)
      conn.commit()
  conn.close() 

