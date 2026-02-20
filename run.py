#!/usr/bin/env python3
"""
Socket Chat Application - Entry Point
"""

import sys
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# Now import
try:
    from chat_app.main import main
except ImportError as e:
    print(f"Error importing chat_app: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Script directory: {SCRIPT_DIR}")
    print(f"Contents of script dir: {os.listdir(SCRIPT_DIR)}")
    sys.exit(1)

if __name__ == "__main__":
    main()