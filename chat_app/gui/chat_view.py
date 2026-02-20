# chat_app/gui/chat_view.py
import tkinter as tk
from tkinter import scrolledtext
import queue
import time

class ChatView:
    """Base chat view component"""
    
    def __init__(self, root, is_server=False):
        self.root = root
        self.is_server = is_server
        self.message_queue = queue.Queue()
        
        # Color scheme
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
        self.process_queue()
        
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Frame(main_frame, bg=self.colors['secondary'], height=60)
        header.pack(fill=tk.X, pady=(0, 15))
        header.pack_propagate(False)
        
        title_text = "SERVER" if self.is_server else "CLIENT"
        self.title_label = tk.Label(header, 
                                   text=title_text,
                                   bg=self.colors['secondary'],
                                   fg=self.colors['highlight'] if self.is_server else self.colors['success'],
                                   font=('Helvetica', 16, 'bold'))
        self.title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.status_label = tk.Label(header,
                                    text="● Disconnected",
                                    bg=self.colors['secondary'],
                                    fg=self.colors['muted'],
                                    font=('Helvetica', 10))
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Connection frame
        conn_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        conn_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Host input
        tk.Label(conn_frame, text="Host:", bg=self.colors['bg'], 
                fg=self.colors['text'], font=('Helvetica', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.host_entry = tk.Entry(conn_frame, width=15, 
                                  bg=self.colors['secondary'],
                                  fg=self.colors['text'],
                                  insertbackground=self.colors['text'],
                                  relief=tk.FLAT,
                                  font=('Helvetica', 10))
        self.host_entry.pack(side=tk.LEFT, padx=(0, 15))
        self.host_entry.insert(0, "127.0.0.1")
        
        # Port input
        tk.Label(conn_frame, text="Port:", bg=self.colors['bg'],
                fg=self.colors['text'], font=('Helvetica', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.port_entry = tk.Entry(conn_frame, width=8,
                                  bg=self.colors['secondary'],
                                  fg=self.colors['text'],
                                  insertbackground=self.colors['text'],
                                  relief=tk.FLAT,
                                  font=('Helvetica', 10))
        self.port_entry.pack(side=tk.LEFT, padx=(0, 15))
        self.port_entry.insert(0, "65432")
        
        # Action button
        action_text = "START SERVER" if self.is_server else "CONNECT"
        self.action_btn = tk.Button(conn_frame, text=action_text,
                                   bg=self.colors['highlight'],
                                   fg=self.colors['text'],
                                   font=('Helvetica', 10, 'bold'),
                                   relief=tk.FLAT,
                                   cursor="hand2",
                                   command=self.toggle_connection)
        self.action_btn.pack(side=tk.LEFT, padx=10)
        
        # Chat display
        chat_container = tk.Frame(main_frame, bg=self.colors['secondary'], bd=2, relief=tk.FLAT)
        chat_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            font=('Consolas', 11),
            padx=15,
            pady=15,
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Configure tags for styling
        self.chat_display.tag_configure("timestamp", foreground=self.colors['muted'], font=('Consolas', 9))
        self.chat_display.tag_configure("received", foreground=self.colors['received'], font=('Consolas', 11, 'bold'))
        self.chat_display.tag_configure("sent", foreground=self.colors['sent'], font=('Consolas', 11, 'bold'))
        self.chat_display.tag_configure("system", foreground=self.colors['success'], font=('Consolas', 10, 'italic'))
        self.chat_display.tag_configure("error", foreground="#ff4757", font=('Consolas', 10, 'bold'))
        
        # Input area
        input_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        input_frame.pack(fill=tk.X)
        
        self.message_entry = tk.Entry(input_frame,
                                     bg=self.colors['secondary'],
                                     fg=self.colors['text'],
                                     insertbackground=self.colors['text'],
                                     relief=tk.FLAT,
                                     font=('Helvetica', 11),
                                     state=tk.DISABLED)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=8)
        
        self.send_btn = tk.Button(input_frame, text="SEND ➤",
                                 bg=self.colors['accent'],
                                 fg=self.colors['text'],
                                 font=('Helvetica', 10, 'bold'),
                                 relief=tk.FLAT,
                                 cursor="hand2",
                                 state=tk.DISABLED,
                                 command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT, ipadx=20, ipady=5)
        
    def add_message(self, text: str, msg_type: str = "system") -> None:
        """Add message to GUI display"""
        timestamp = time.strftime("%H:%M:%S")
        self.chat_display.config(state=tk.NORMAL)
        
        if msg_type == "received":
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.chat_display.insert(tk.END, "← ", "received")
            self.chat_display.insert(tk.END, f"{text}\n", "received")
        elif msg_type == "sent":
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.chat_display.insert(tk.END, "→ ", "sent")
            self.chat_display.insert(tk.END, f"{text}\n", "sent")
        elif msg_type == "error":
            self.chat_display.insert(tk.END, f"[{timestamp}] ⚠ ", "error")
            self.chat_display.insert(tk.END, f"{text}\n", "error")
        else:
            self.chat_display.insert(tk.END, f"[{timestamp}] ℹ ", "system")
            self.chat_display.insert(tk.END, f"{text}\n", "system")
            
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
    def process_queue(self):
        """Process message queue for thread-safe GUI updates"""
        try:
            while True:
                msg, msg_type = self.message_queue.get_nowait()
                self.add_message(msg, msg_type)
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)
        
    def queue_message(self, text: str, msg_type: str = "system") -> None:
        """Add message to queue"""
        self.message_queue.put((text, msg_type))
        
    def toggle_connection(self):
        pass
        
    def send_message(self):
        pass
        
    def update_ui_state(self, connected: bool, is_server: bool = False):
        """Update UI based on connection state"""
        if connected:
            self.action_btn.config(text="STOP SERVER" if is_server else "DISCONNECT", bg="#ff4757")
            self.host_entry.config(state=tk.DISABLED)
            self.port_entry.config(state=tk.DISABLED)
            self.status_label.config(text="● Connected" if not is_server else "● Waiting", 
                                   fg=self.colors['success'] if not is_server else "#ffa502")
            self.message_entry.config(state=tk.NORMAL)
            self.send_btn.config(state=tk.NORMAL)
        else:
            self.action_btn.config(text="START SERVER" if is_server else "CONNECT", 
                                 bg=self.colors['highlight'])
            self.host_entry.config(state=tk.NORMAL)
            self.port_entry.config(state=tk.NORMAL)
            self.status_label.config(text="● Disconnected", fg=self.colors['muted'])
            self.message_entry.config(state=tk.DISABLED)
            self.send_btn.config(state=tk.DISABLED)