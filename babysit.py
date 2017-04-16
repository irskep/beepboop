#!/usr/bin/env python3
"""
Repeatedly runs the command given until you ctrl+c this program.

Example:

    # Every time you quit your game, it will be launched again
    # until you ctrl+c babysit.py
    ./babysit.py python my_game.py
"""
import sys
import subprocess
from math import floor

cmd = sys.argv[1:]

message = '<NEW BABYSIT SESSION>'
left_padding = floor((78 - len(message)) / 2)
right_padding = 78 - len(message) - left_padding

cont = True
while cont:
  print('-' * left_padding + message + '-' * right_padding, file=sys.stderr)
  p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
  try:
    p.wait()
  except KeyboardInterrupt:
    cont = False
