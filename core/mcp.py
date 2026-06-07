#!/usr/bin/env python3

import json
import sys
import inspect
from typing import Annotated, get_args, get_origin

def get_flag(key: Annotated[str,"Use the key '456' to get a flag"]):
  if key == "456":
    return "Ok: FLAG{123-456-789}"
  else:
    return "Nope"

get_flag.__doc__ = "Use this function to get a flag!"

GLOBAL_FNS = [get_flag]

def fn_to_tool_json(fn,tag=None):
    """
    Convert an annotated Python function into an OpenAI Responses API tool schema.
    """
    sig = inspect.signature(fn)

    properties = {}
    required = []

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    SKIP_FIRST = False
    # arglist = sig.parameters.items()
    # if tag is not None:
    #   arglist = arglist[1:]
    for name, param in sig.parameters.items():
      if tag is not None and SKIP_FIRST is False:
        SKIP_FIRST = True
        continue
      annotation = param.annotation
      description = ""
      py_type = str
      # Handle Annotated[T, "description"]
      if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        py_type = args[0]
        if len(args) > 1:
          description = args[1]
      else:
        py_type = annotation

      json_type = type_map.get(py_type, "string")

      properties[name] = {
        "type": json_type,
        "description": description,
      }

      if param.default is inspect.Parameter.empty:
        required.append(name)

    fn_name = fn.__name__
    if tag is not None:
      fn_name += "-" + tag

    return {
      "type": "function",
      "name": fn_name,
      "description": inspect.getdoc(fn) or "",
      "inputSchema": {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
      },
    }

def send(message: dict) -> None:
  sys.stdout.write(json.dumps(message) + "\n")
  sys.stdout.flush()

def handle_request(request):
  global GLOBAL_FNS
  method = request.get("method")
  request_id = request.get("id")
  if method == "initialize":
    send({
      "jsonrpc": "2.0",
      "id": request_id,
      "result": {
        "protocolVersion": "2024-11-05",
        "serverInfo": {
          "name": "vaporeon",
          "version": "0.0.1"
        },
        "capabilities": {
          "tools": {}
        }
      }
    })
  elif method == "tools/list":
    send({
      "jsonrpc": "2.0",
      "id": request_id,
      "result": {
        "tools": [fn_to_tool_json(f) for f in GLOBAL_FNS]
      }
    })
  elif method == "tools/call":
    params = request.get("params", {})
    tool_name = params.get("name")
    tool_args = params.get("arguments")
    # sys.stderr.write(json.dumps(request,indent=2))
    tool_fn = None
    for t in GLOBAL_FNS:
      if t.__name__ == tool_name:
        tool_fn = t
        break
    result = tool_fn(**tool_args)
    send({
      "jsonrpc": "2.0",
      "id": request_id,
      "result": {
        "content": [
          {
            "type": "text",
            "text": result
          }
        ]
      }
    })

def start_mcp():
  for line in sys.stdin:
    line = line.strip()
    if not line:
      continue
    request = json.loads(line)
    handle_request(request)
