# chat_app/utils/logger.py
import sys
import time
from typing import Optional, Callable, Any

class DualOutput:
    """Helper class to output to both GUI and terminal"""
    
    def __init__(self, 
                 gui_add_message_func: Callable[[str, str], None], 
                 db_manager: Optional[Any] = None, 
                 session_id: Optional[int] = None):
        self.gui_add_message = gui_add_message_func
        self.db_manager = db_manager
        self.session_id = session_id
        
    def set_session(self, session_id: int) -> None:
        """Set current session ID"""
        self.session_id = session_id
        
    def output(self, text: str, msg_type: str = "system", sender: Optional[str] = None) -> None:
        """Output to terminal, database, and GUI"""
        # Print to terminal with timestamp
        timestamp = time.strftime("%H:%M:%S")
        prefix = {
            "received": "[RECV]",
            "sent": "[SENT]",
            "error": "[ERROR]",
            "system": "[INFO]"
        }.get(msg_type, "[INFO]")
        
        print(f"[{timestamp}] {prefix} {text}")
        sys.stdout.flush()  # Ensure immediate output
        
        # Save to database
        if self.db_manager and self.session_id and sender:
            self.db_manager.save_message(self.session_id, sender, text, msg_type)
        
        # Add to GUI queue
        self.gui_add_message(text, msg_type)

def setup_logging():
    """Setup basic logging configuration"""
    pass  # Placeholder for future logging setup