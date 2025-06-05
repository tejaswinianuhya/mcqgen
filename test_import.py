# test_import.py
import os
import sys
print("sys.executable:", sys.executable)
print("sys.path:", sys.path)
import langchain
print("langchain location:", langchain.__file__)