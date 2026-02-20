# chat_app/database/chat_db.py
import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional

class ChatDatabase:
    """SQLite database manager for chat history"""
    
    def __init__(self, db_file: str = "chat_history.db"):
        self.db_file = db_file
        self.init_database()
        
    def init_database(self) -> None:
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_type TEXT NOT NULL,
                host TEXT,
                port INTEGER,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                msg_type TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def create_session(self, session_type: str, host: str, port: int) -> int:
        """Create new chat session"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_sessions (session_type, host, port, status)
            VALUES (?, ?, ?, 'active')
        ''', (session_type, host, port))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id
        
    def end_session(self, session_id: int) -> None:
        """Mark session as ended"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE chat_sessions 
            SET ended_at = CURRENT_TIMESTAMP, status = 'ended'
            WHERE id = ?
        ''', (session_id,))
        conn.commit()
        conn.close()
        
    def save_message(self, session_id: int, sender: str, message: str, msg_type: str) -> None:
        """Save message to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_messages (session_id, sender, message, msg_type)
            VALUES (?, ?, ?, ?)
        ''', (session_id, sender, message, msg_type))
        conn.commit()
        conn.close()
        
    def get_session_history(self, session_id: int) -> List[Tuple]:
        """Get all messages from a session"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, sender, message, msg_type 
            FROM chat_messages 
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))
        results = cursor.fetchall()
        conn.close()
        return results
        
    def get_all_sessions(self) -> List[Tuple]:
        """Get all chat sessions"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, session_type, host, port, started_at, ended_at, status
            FROM chat_sessions
            ORDER BY started_at DESC
        ''')
        results = cursor.fetchall()
        conn.close()
        return results
        
    def search_messages(self, keyword: str) -> List[Tuple]:
        """Search messages by keyword"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.timestamp, m.sender, m.message, m.msg_type, s.session_type
            FROM chat_messages m
            JOIN chat_sessions s ON m.session_id = s.id
            WHERE m.message LIKE ?
            ORDER BY m.timestamp DESC
        ''', (f'%{keyword}%',))
        results = cursor.fetchall()
        conn.close()
        return results
        
    def delete_session(self, session_id: int) -> None:
        """Delete a session and its messages"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
        conn.commit()
        conn.close()
        
    def get_db_path(self) -> str:
        """Get absolute path to database file"""
        return os.path.abspath(self.db_file)