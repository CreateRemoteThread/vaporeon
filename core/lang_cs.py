#!/usr/bin/env python3

def _get_node_text(node,cs_src):
  return cs_src[node.start_byte:node.end_byte]

def _extract_calls(fn,cs_src,parent,parent_name,db,parser):
  tree = parser.parse(cs_src)
  def visit(node):
    if node.type == "invocation_expression":
      func_node = node.child_by_field_name("function")
      if func_node.type == "member_access_expression":
        name_node = func_node.child_by_field_name("name")
        func_name = _get_node_text(name_node,cs_src).decode("utf-8").strip()
      else:
        func_name = _get_node_text(func_node,cs_src).decode("utf-8").strip()
      db.execute("INSERT INTO calls (srcid,src, dest) VALUES (?,?,?)",(parent,parent_name,func_name))
    for child in node.children:
      visit(child)
  visit(tree.root_node)

def _extract_functions(fn,cs_src,db,parser):
  tree = parser.parse(cs_src)
  functions = []
  def visit(node):
    if node.type == "method_declaration":
      name_node = node.child_by_field_name("name")
      function_name = _get_node_text(name_node,cs_src).decode("utf-8").strip()
      if function_name is None:
        function_name = "<unknown>"
      else:
        function_name = function_name.strip()
      node_text = _get_node_text(node,cs_src)
      db.execute("INSERT INTO functions (name,file,start,end) VALUES (?,?,?,?)",(function_name,fn,node.start_byte, node.end_byte))
      _extract_calls(fn,node_text,parent=db.lastrowid,parent_name=function_name,db=db,parser=parser)
      # __internal_print(_extract_calls(_get_node_text(node, cs_src)))
    for child in node.children:
      visit(child)
  visit(tree.root_node)

if __name__ == "__main__":
  print("error: you probably want /r/vibecoding instead")
