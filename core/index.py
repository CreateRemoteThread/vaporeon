#!/usr/bin/env python3

import sqlite3
import sys
from typing import Annotated

conn = None
cur = None

def _load_db(filename):
  global conn, cur
  conn = sqlite3.connect(filename)
  cur = conn.cursor()

