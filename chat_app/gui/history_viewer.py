# chat_app/gui/history_viewer.py
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk

class HistoryViewer:
    """Window to view chat history"""
    
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Chat History")
        self.window.geometry("800x600")
        self.window.configure(bg="#1a1a2e")
        
        self.colors = {
            'bg': "#1a1a2e",
            'secondary': "#16213e",
            'accent': "#0f3460",
            'highlight': "#e94560",
            'text': "#eaeaea",
            'muted': "#a0a0a0",
            'success': "#00d9ff",
            'received': "#4ecca3",
            'sent': "#e94560"
        }
        
        self.create_widgets()
        self.load_sessions()
        
    def create_widgets(self):
        # Top frame with search
        top_frame = tk.Frame(self.window, bg=self.colors['bg'])
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(top_frame, text="Search:", bg=self.colors['bg'], 
                fg=self.colors['text'], font=('Helvetica', 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_entry = tk.Entry(top_frame, width=30,
                                    bg=self.colors['secondary'],
                                    fg=self.colors['text'],
                                    insertbackground=self.colors['text'],
                                    relief=tk.FLAT)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.search())
        
        tk.Button(top_frame, text="Search",
                 bg=self.colors['accent'],
                 fg=self.colors['text'],
                 relief=tk.FLAT,
                 command=self.search).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="Refresh",
                 bg=self.colors['success'],
                 fg=self.colors['bg'],
                 relief=tk.FLAT,
                 command=self.load_sessions).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="Delete Selected",
                 bg=self.colors['highlight'],
                 fg=self.colors['text'],
                 relief=tk.FLAT,
                 command=self.delete_selected).pack(side=tk.RIGHT, padx=5)
        
        # Paned window for split view
        paned = tk.PanedWindow(self.window, orient=tk.HORIZONTAL, bg=self.colors['bg'])
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Sessions list (left side)
        left_frame = tk.Frame(paned, bg=self.colors['bg'])
        paned.add(left_frame, width=250)
        
        tk.Label(left_frame, text="Chat Sessions", 
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
        
        # Treeview for sessions
        columns = ('ID', 'Type', 'Host:Port', 'Date')
        self.session_list = ttk.Treeview(left_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.session_list.heading(col, text=col)
            
        self.session_list.column('ID', width=30)
        self.session_list.column('Type', width=60)
        self.session_list.column('Host:Port', width=100)
        self.session_list.column('Date', width=120)
        
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.session_list.yview)
        self.session_list.configure(yscrollcommand=scrollbar.set)
        
        self.session_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.session_list.bind('<<TreeviewSelect>>', self.on_session_select)
        
        # Chat display (right side)
        right_frame = tk.Frame(paned, bg=self.colors['bg'])
        paned.add(right_frame, width=500)
        
        tk.Label(right_frame, text="Messages", 
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
        
        self.chat_display = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Consolas', 10),
            padx=10,
            pady=10,
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        for tag, color in [("timestamp", self.colors['muted']), 
                          ("received", self.colors['received']),
                          ("sent", self.colors['sent']),
                          ("system", self.colors['success']),
                          ("error", "#ff4757")]:
            self.chat_display.tag_configure(tag, foreground=color)
            
    def load_sessions(self):
        """Load all sessions into the list"""
        for item in self.session_list.get_children():
            self.session_list.delete(item)
            
        sessions = self.db_manager.get_all_sessions()
        for session in sessions:
            session_id, sess_type, host, port, started, ended, status = session
            host_port = f"{host}:{port}" if host and port else "N/A"
            date_str = started[:16] if started else "Unknown"
            self.session_list.insert('', tk.END, values=(session_id, sess_type, host_port, date_str))
            
    def on_session_select(self, event=None):
        """Display selected session messages"""
        selection = self.session_list.selection()
        if not selection:
            return
            
        item = self.session_list.item(selection[0])
        session_id = item['values'][0]
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        
        messages = self.db_manager.get_session_history(session_id)
        
        if not messages:
            self.chat_display.insert(tk.END, "No messages in this session.\n", "system")
        else:
            for msg in messages:
                timestamp, sender, message, msg_type = msg
                time_str = timestamp[11:19] if timestamp else "???"
                
                self.chat_display.insert(tk.END, f"[{time_str}] ", "timestamp")
                
                if msg_type == "received":
                    self.chat_display.insert(tk.END, f"← {sender}: ", "received")
                    self.chat_display.insert(tk.END, f"{message}\n", "received")
                elif msg_type == "sent":
                    self.chat_display.insert(tk.END, f"→ {sender}: ", "sent")
                    self.chat_display.insert(tk.END, f"{message}\n", "sent")
                else:
                    self.chat_display.insert(tk.END, f"ℹ {message}\n", "system")
                    
        self.chat_display.config(state=tk.DISABLED)
        
    def search(self):
        """Search messages"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Search", "Please enter a search term")
            return
            
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        
        results = self.db_manager.search_messages(keyword)
        
        if not results:
            self.chat_display.insert(tk.END, f"No messages found containing '{keyword}'\n", "system")
        else:
            self.chat_display.insert(tk.END, f"Found {len(results)} messages:\n\n", "system")
            for msg in results:
                timestamp, sender, message, msg_type, sess_type = msg
                self.chat_display.insert(tk.END, f"[{timestamp}] ({sess_type}) {sender}: ", "system")
                
                # Simple highlight
                self.chat_display.insert(tk.END, f"{message}\n", msg_type if msg_type in ["received", "sent"] else "system")
                
        self.chat_display.config(state=tk.DISABLED)
        
    def delete_selected(self):
        """Delete selected session"""
        selection = self.session_list.selection()
        if not selection:
            messagebox.showwarning("Delete", "Please select a session to delete")
            return
            
        item = self.session_list.item(selection[0])
        session_id = item['values'][0]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Delete session {session_id}? This cannot be undone."):
            self.db_manager.delete_session(session_id)
            self.load_sessions()
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.insert(tk.END, "Session deleted.\n", "system")
            self.chat_display.config(state=tk.DISABLED)