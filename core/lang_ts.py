#!/usr/bin/env python3

def _get_node_text(node,ts_src):
  return ts_src[node.start_byte:node.end_byte]

def _extract_calls(fn,ts_src,parent,parent_name,db,parser):
  tree = parser.parse(ts_src)
  # calls = []
  def visit(node):
    if node.type == "call_expression":
      function_node = node.child_by_field_name("function")
      arguments_node = node.child_by_field_name("arguments")
      if function_node:
        fn_dest = _get_node_text(function_node,ts_src).decode("utf-8").strip()
      else:
        fn_dest = "<unknown>"
      db.execute("INSERT INTO calls (srcid,src, dest) VALUES (?,?,?)",(parent,parent_name,fn_dest))
      # calls.append({
      #   "name":_get_node_text(function_node,ts_src) if function_node else None,
      #   "expression":_get_node_text(node,ts_src)
      # })
    for child in node.children:
      visit(child)
  visit(tree.root_node)
  # return calls

def _extract_functions(fn,ts_src,db,parser):
  tree = parser.parse(ts_src)
  def find_name(node):
    name_node = node.child_by_field_name("name")
    if name_node:
      return _get_node_text(name_node,ts_src).decode("utf-8")
    parent = node.parent
    if parent and parent.type == "variable_declarator":
      name_node = parent.child_by_field_name("name")
      if name_node:
        return _get_node_text(name_node,ts_src).decode("utf-8")
    elif parent and parent.type == "pair":
      key_node = parent.child_by_field_name("key")
      if key_node:
        return _get_node_text(key_node,ts_src).decode("utf-8")
    return "<anonymous>"
  def visit(node):
    function_node_types = {
      "function_declaration",
      "function_expression",
      "arrow_function",
      "method_definition",
      "method_signature"
    }
    if node.type in function_node_types:
      function_name = find_name(node)
      node_text = _get_node_text(node,ts_src)
      db.execute("INSERT INTO functions (name,file,start,end) VALUES (?,?,?,?)",(function_name,fn,node.start_byte, node.end_byte))
      _extract_calls(fn,node_text,parent=db.lastrowid,parent_name=function_name,db=db,parser=parser)
    for child in node.children:
      visit(child)
  visit(tree.root_node)

if __name__ == "__main__":
  print("error: you probably want /r/vibecoding instead")
