#!/usr/bin/env python3


def _get_node_text(node,c_src):
  return c_src[node.start_byte:node.end_byte]

def _extract_calls(fn,c_src,parent,parent_name,db,parser):
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

def _extract_functions(fn,c_src,db,parser):
  tree = parser.parse(c_src)
  functions = []
  def visit(node):
    if node.type == "function_definition":
      declarator = node.child_by_field_name("declarator")
      function_name = None
      # Walk down nested declarators to find the identifier
      def find_identifier(n):
        if n.type == "identifier":
          return _get_node_text(n, c_src).decode("utf-8")
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
        function_name = function_name.strip()
      node_text = _get_node_text(node,c_src)
      db.execute("INSERT INTO functions (name,file,start,end) VALUES (?,?,?,?)",(function_name,fn,node.start_byte, node.end_byte))
      # functions.append({
      #   "name": function_name,
      #   "start_line": node.start_point[0] + 1,
      #   "end_line": node.end_point[0] + 1,
      #   "source": node_text,
      # })
      _extract_calls(fn,node_text,parent=db.lastrowid,parent_name=function_name,db=db,parser=parser)
      # __internal_print(_extract_calls(_get_node_text(node, c_src)))
    for child in node.children:
      visit(child)
  visit(tree.root_node)

if __name__ == "__main__":
  print("error: you probably want /r/vibecoding instead")
