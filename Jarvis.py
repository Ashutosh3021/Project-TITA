#!/usr/bin/env python3
"""
JARVIS - Main Entry Point
Run this file to start JARVIS: python Jarvis.py
"""

import sys
import os

# Add JARVIS package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run main
from JARVIS.main import main

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
