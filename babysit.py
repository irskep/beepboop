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

cmd = sys.argv[1:]


cont = True
while cont:
  p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
  try:
    p.wait()
  except KeyboardInterrupt:
    cont = False
