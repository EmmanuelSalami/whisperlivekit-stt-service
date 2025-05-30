#!/usr/bin/env python3
import sys
import os

print("=== DEBUG: sys.argv Analysis ===")
print(f"sys.argv = {sys.argv}")
print(f"len(sys.argv) = {len(sys.argv)}")
for i, arg in enumerate(sys.argv):
    print(f"sys.argv[{i}] = '{arg}'")

print(f"\n=== Environment Info ===")
print(f"__file__ = {__file__}")
print(f"sys.executable = {sys.executable}")
print(f"Working directory = {os.getcwd()}")

# Try to import and see what happens
try:
    from whisperlivekit import parse_args
    print(f"\n=== Trying parse_args() ===")
    args = parse_args()
    print(f"parse_args() succeeded: {args}")
except Exception as e:
    print(f"parse_args() failed: {e}")
    print(f"Exception type: {type(e)}") 