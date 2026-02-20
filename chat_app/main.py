#!/usr/bin/env python3
"""
Main entry point for chat application
"""

import sys
import os

# Add parent directory to path when running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat_app.database import ChatDatabase
from chat_app.gui import ModeSelector

def main():
    """Main entry point"""
    # Initialize database
    db_manager = ChatDatabase()
    print(f"Database initialized: {db_manager.get_db_path()}")
    
    # Start mode selector
    app = ModeSelector(db_manager)
    app.run()

if __name__ == "__main__":
    main()