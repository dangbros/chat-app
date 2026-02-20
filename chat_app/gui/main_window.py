# chat_app/gui/main_window.py
import tkinter as tk
from tkinter import messagebox, simpledialog
from .chat_view import ChatView
from .history_viewer import HistoryViewer
from ..utils.logger import DualOutput
from ..utils.crypto import XorCipher, get_cipher, set_global_key
from ..network.server import ChatServer
from ..network.client import ChatClient

class ModeSelector:
    """Initial mode selection dialog"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.root = tk.Tk()
        self.root.title("VAULT-TEC TERMINAL // MODE SELECT")
        self.root.geometry("400x420")  # Taller for key input and toggle
        self.root.configure(bg="#050b05")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 200
        y = (self.root.winfo_screenheight() // 2) - 210
        self.root.geometry(f"+{x}+{y}")
        self._title_glow_index = 0
        self._title_glow = ["#39d939", "#66ff66", "#98ff98", "#66ff66"]
        self._matrix_frames = [
            "01001010 11001010 00101101",
            "10101100 01001110 11010001",
            "00110011 11100001 01011010",
            "11000101 00011110 10110011",
        ]
        self._matrix_idx = 0
        
        self.create_widgets()
        
    def create_widgets(self):
        self.title_label = tk.Label(self.root, text="FALLOUT TERMINAL",
                                    bg="#050b05", fg="#25d225",
                                    font=('Courier', 24, 'bold'))
        self.title_label.pack(pady=(20, 4))

        self.matrix_label = tk.Label(self.root, text="MATRIX-LINK ENCRYPTION ACTIVE",
                                     bg="#050b05", fg="#66ff66",
                                     font=('Courier', 10))
        self.matrix_label.pack(pady=(0, 10))
        
        # Encryption key input frame
        key_frame = tk.Frame(self.root, bg="#050b05")
        key_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(key_frame, text="Encryption Key:", 
                bg="#050b05", fg="#7CFF7C",
                font=('Helvetica', 10)).pack(anchor=tk.W)
        
        # Entry and toggle button frame
        entry_frame = tk.Frame(key_frame, bg="#050b05")
        entry_frame.pack(fill=tk.X, pady=5)
        
        self.key_entry = tk.Entry(entry_frame, show="•",
                                 bg="#081408", fg="#7CFF7C",
                                 insertbackground="#7CFF7C",
                                 relief=tk.FLAT, font=('Helvetica', 10))
        self.key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.key_entry.insert(0, "my_secret_key_2024")
        
        # Show/Hide toggle button
        self.show_key = False
        self.toggle_btn = tk.Button(entry_frame, text="👁",
                                   bg="#081408", fg="#66ff66",
                                   font=('Helvetica', 10),
                                   relief=tk.FLAT,
                                   cursor="hand2",
                                   command=self.toggle_key_visibility,
                                   width=3)
        self.toggle_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Key info label
        tk.Label(key_frame, text="Both sides must use the same key!",
                bg="#050b05", fg="#2f7f2f",
                font=('Helvetica', 8)).pack(anchor=tk.W)
        
        # Generate random key button
        tk.Button(key_frame, text="🎲 GENERATE KEY",
                 bg="#0f2d0f", fg="#7CFF7C",
                 font=('Helvetica', 9),
                 relief=tk.FLAT,
                 cursor="hand2",
                 command=self.generate_random_key).pack(anchor=tk.W, pady=(5, 0))
        
        tk.Label(self.root, text="CHOOSE TERMINAL MODE",
                bg="#050b05", fg="#2f7f2f",
                font=('Helvetica', 12)).pack(pady=(20, 10))
        
        btn_frame = tk.Frame(self.root, bg="#050b05")
        btn_frame.pack(pady=10)
        
        self.server_btn = tk.Button(btn_frame, text="BOOT SERVER",
                                    bg="#25d225", fg="#050b05",
                                    font=('Courier', 12, 'bold'),
                                    relief=tk.FLAT,
                                    activebackground="#66ff66",
                                    cursor="hand2",
                                    width=20, height=2,
                                    command=self.start_server)
        self.server_btn.pack(pady=10)

        self.client_btn = tk.Button(btn_frame, text="BOOT CLIENT",
                                    bg="#0f2d0f", fg="#66ff66",
                                    activebackground="#1f541f",
                                    font=('Courier', 12, 'bold'),
                                    relief=tk.FLAT,
                                    cursor="hand2",
                                    width=20, height=2,
                                    command=self.start_client)
        self.client_btn.pack(pady=10)

        self.animate_terminal_intro()

    def animate_terminal_intro(self):
        """Animate the mode selector with subtle retro effects."""
        self._title_glow_index = (self._title_glow_index + 1) % len(self._title_glow)
        glow = self._title_glow[self._title_glow_index]
        self.title_label.config(fg=glow)
        self.server_btn.config(bg=glow)

        self._matrix_idx = (self._matrix_idx + 1) % len(self._matrix_frames)
        self.matrix_label.config(text=f"MATRIX-LINK ENCRYPTION ACTIVE :: {self._matrix_frames[self._matrix_idx]}")
        self.root.after(320, self.animate_terminal_intro)
        
    def toggle_key_visibility(self):
        """Toggle between showing and hiding the encryption key"""
        self.show_key = not self.show_key
        if self.show_key:
            self.key_entry.config(show="")
            self.toggle_btn.config(text="🙈", fg="#25d225")
        else:
            self.key_entry.config(show="•")
            self.toggle_btn.config(text="👁", fg="#66ff66")
            
    def generate_random_key(self):
        """Generate a random encryption key"""
        import secrets
        import string
        # Generate 16-character random key
        random_key = ''.join(secrets.choice(string.ascii_letters + string.digits + "_-") for _ in range(16))
        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(0, random_key)
        # Show the key temporarily
        self.key_entry.config(show="")
        self.show_key = True
        self.toggle_btn.config(text="🙈", fg="#25d225")
        self.root.after(2000, self.hide_key_temporarily)
        
    def hide_key_temporarily(self):
        """Auto-hide key after showing generated key"""
        if self.show_key:
            self.toggle_key_visibility()
        
    def get_key(self):
        """Get encryption key from input"""
        key = self.key_entry.get().strip()
        if not key:
            key = "default_key_123"
        return key
        
    def start_server(self):
        key = self.get_key()
        set_global_key(key)
        masked_key = key[:3] + '*' * (len(key) - 6) + key[-3:] if len(key) > 6 else '*' * len(key)
        print(f"\nEncryption Key: {masked_key}")
        print("="*50)
        print("STARTING SERVER MODE")
        print("="*50 + "\n")
        self.root.destroy()
        root = tk.Tk()
        app = ServerGUI(root, self.db_manager)
        root.mainloop()
        
    def start_client(self):
        key = self.get_key()
        set_global_key(key)
        masked_key = key[:3] + '*' * (len(key) - 6) + key[-3:] if len(key) > 6 else '*' * len(key)
        print(f"\nEncryption Key: {masked_key}")
        print("="*50)
        print("STARTING CLIENT MODE")
        print("="*50 + "\n")
        self.root.destroy()
        root = tk.Tk()
        app = ClientGUI(root, self.db_manager)
        root.mainloop()
        
    def run(self):
        self.root.mainloop()


class ServerGUI(ChatView):
    """Server GUI implementation with encryption"""
    
    def __init__(self, root, db_manager=None):
        super().__init__(root, is_server=True)
        self.db_manager = db_manager
        self.session_id = None
        self.server = None
        self.cipher = get_cipher()
        
        # Add history and key change buttons
        self.add_extra_buttons()
        
        # Setup logger
        self.logger = DualOutput(self.queue_message, db_manager, None)
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
    def add_extra_buttons(self):
        """Add history and key buttons to connection frame"""
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):
                        btn_frame = tk.Frame(child, bg=self.colors['bg'])
                        btn_frame.pack(side=tk.RIGHT, padx=5)
                        
                        tk.Button(btn_frame, text="🔐 Key",
                                 bg="#c4ff6f", fg="#050b05",
                                 font=('Helvetica', 9, 'bold'),
                                 relief=tk.FLAT,
                                 cursor="hand2",
                                 command=self.change_key).pack(side=tk.LEFT, padx=2)
                        
                        tk.Button(btn_frame, text="📜 History",
                                 bg=self.colors['accent'],
                                 fg=self.colors['text'],
                                 font=('Helvetica', 9),
                                 relief=tk.FLAT,
                                 cursor="hand2",
                                 command=self.open_history).pack(side=tk.LEFT, padx=2)
                        break
                break
                
    def change_key(self):
        """Change encryption key with show/hide option"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Encryption Key")
        dialog.geometry("300x150")
        dialog.configure(bg="#050b05")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Enter new encryption key:", 
                bg="#050b05", fg="#7CFF7C").pack(pady=10)
        
        # Entry frame with toggle
        entry_frame = tk.Frame(dialog, bg="#050b05")
        entry_frame.pack(pady=5, padx=20, fill=tk.X)
        
        key_var = tk.StringVar(value=self.cipher.key)
        key_entry = tk.Entry(entry_frame, textvariable=key_var, show="•",
                            bg="#081408", fg="#7CFF7C",
                            insertbackground="#7CFF7C",
                            relief=tk.FLAT)
        key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        key_entry.select_range(0, tk.END)
        
        def toggle_show():
            if key_entry.cget('show') == "•":
                key_entry.config(show="")
                toggle_btn.config(text="🙈", fg="#25d225")
            else:
                key_entry.config(show="•")
                toggle_btn.config(text="👁", fg="#66ff66")
        
        toggle_btn = tk.Button(entry_frame, text="👁", 
                              bg="#081408", fg="#66ff66",
                              relief=tk.FLAT, cursor="hand2",
                              command=toggle_show, width=3)
        toggle_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        def apply_key():
            new_key = key_var.get().strip()
            if new_key:
                self.cipher.set_key(new_key)
                if self.server:
                    self.server.set_encryption_key(new_key)
                self.logger.output(f"Encryption key changed", "system", "System")
                dialog.destroy()
        
        tk.Button(dialog, text="Apply", bg="#66ff66", fg="#050b05",
                 font=('Helvetica', 10, 'bold'),
                 relief=tk.FLAT, command=apply_key).pack(pady=15)
        
        key_entry.focus()
        key_entry.bind('<Return>', lambda e: apply_key())
                
    def open_history(self):
        """Open history viewer"""
        if self.db_manager:
            HistoryViewer(self.root, self.db_manager)
        else:
            messagebox.showwarning("History", "Database not available")
        
    def toggle_connection(self):
        if not self.server or not self.server.running:
            self.start_server()
        else:
            self.stop_server()
            
    def start_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        
        # Create database session
        if self.db_manager:
            self.session_id = self.db_manager.create_session("server", host, port)
            self.logger.set_session(self.session_id)
        
        # Create server instance with cipher
        self.server = ChatServer(
            host, port, self.logger,
            on_connect=self.on_client_connect,
            on_disconnect=self.on_client_disconnect,
            on_receive=lambda msg: None,
            cipher=self.cipher
        )
        
        if self.server.start():
            self.update_ui_state(True, is_server=True)
            
    def on_client_connect(self, addr):
        """Callback when client connects"""
        self.root.after(0, lambda: self.status_label.config(
            text="● Connected", fg=self.colors['success']))
        
    def on_client_disconnect(self):
        """Callback when client disconnects"""
        self.root.after(0, lambda: self.status_label.config(
            text="● Waiting", fg="#c4ff6f"))
        self.root.after(0, lambda: self.message_entry.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.send_btn.config(state=tk.DISABLED))
            
    def send_message(self):
        if self.server and self.message_entry.get():
            self.server.send(self.message_entry.get())
            self.message_entry.delete(0, tk.END)
                    
    def stop_server(self):
        if self.server:
            self.server.stop()
            
        if self.db_manager and self.session_id:
            self.db_manager.end_session(self.session_id)
            self.session_id = None
            
        self.update_ui_state(False, is_server=True)


class ClientGUI(ChatView):
    """Client GUI implementation with encryption"""
    
    def __init__(self, root, db_manager=None):
        super().__init__(root, is_server=False)
        self.db_manager = db_manager
        self.session_id = None
        self.client = None
        self.cipher = get_cipher()
        
        # Add history and key buttons
        self.add_extra_buttons()
        
        # Setup logger
        self.logger = DualOutput(self.queue_message, db_manager, None)
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
    def add_extra_buttons(self):
        """Add history and key buttons to connection frame"""
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):
                        btn_frame = tk.Frame(child, bg=self.colors['bg'])
                        btn_frame.pack(side=tk.RIGHT, padx=5)
                        
                        tk.Button(btn_frame, text="🔐 Key",
                                 bg="#c4ff6f", fg="#050b05",
                                 font=('Helvetica', 9, 'bold'),
                                 relief=tk.FLAT,
                                 cursor="hand2",
                                 command=self.change_key).pack(side=tk.LEFT, padx=2)
                        
                        tk.Button(btn_frame, text="📜 History",
                                 bg=self.colors['accent'],
                                 fg=self.colors['text'],
                                 font=('Helvetica', 9),
                                 relief=tk.FLAT,
                                 cursor="hand2",
                                 command=self.open_history).pack(side=tk.LEFT, padx=2)
                        break
                break
                
    def change_key(self):
        """Change encryption key with show/hide option"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Encryption Key")
        dialog.geometry("300x150")
        dialog.configure(bg="#050b05")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Enter new encryption key:", 
                bg="#050b05", fg="#7CFF7C").pack(pady=10)
        
        # Entry frame with toggle
        entry_frame = tk.Frame(dialog, bg="#050b05")
        entry_frame.pack(pady=5, padx=20, fill=tk.X)
        
        key_var = tk.StringVar(value=self.cipher.key)
        key_entry = tk.Entry(entry_frame, textvariable=key_var, show="•",
                            bg="#081408", fg="#7CFF7C",
                            insertbackground="#7CFF7C",
                            relief=tk.FLAT)
        key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        key_entry.select_range(0, tk.END)
        
        def toggle_show():
            if key_entry.cget('show') == "•":
                key_entry.config(show="")
                toggle_btn.config(text="🙈", fg="#25d225")
            else:
                key_entry.config(show="•")
                toggle_btn.config(text="👁", fg="#66ff66")
        
        toggle_btn = tk.Button(entry_frame, text="👁", 
                              bg="#081408", fg="#66ff66",
                              relief=tk.FLAT, cursor="hand2",
                              command=toggle_show, width=3)
        toggle_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        def apply_key():
            new_key = key_var.get().strip()
            if new_key:
                self.cipher.set_key(new_key)
                if self.client:
                    self.client.set_encryption_key(new_key)
                self.logger.output(f"Encryption key changed", "system", "System")
                dialog.destroy()
        
        tk.Button(dialog, text="Apply", bg="#66ff66", fg="#050b05",
                 font=('Helvetica', 10, 'bold'),
                 relief=tk.FLAT, command=apply_key).pack(pady=15)
        
        key_entry.focus()
        key_entry.bind('<Return>', lambda e: apply_key())
                
    def open_history(self):
        """Open history viewer"""
        if self.db_manager:
            HistoryViewer(self.root, self.db_manager)
        else:
            messagebox.showwarning("History", "Database not available")
        
    def toggle_connection(self):
        if not self.client or not self.client.running:
            self.connect_to_server()
        else:
            self.disconnect()
            
    def connect_to_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        
        # Create database session
        if self.db_manager:
            self.session_id = self.db_manager.create_session("client", host, port)
            self.logger.set_session(self.session_id)
        
        # Create client instance with cipher
        self.client = ChatClient(
            host, port, self.logger,
            on_connect=self.on_connect,
            on_disconnect=self.on_disconnect,
            on_receive=lambda msg: None,
            cipher=self.cipher
        )
        
        if self.client.connect():
            self.update_ui_state(True, is_server=False)
            
    def on_connect(self):
        """Callback when connected"""
        pass
        
    def on_disconnect(self):
        """Callback when disconnected"""
        self.root.after(0, lambda: self.update_ui_state(False, is_server=False))
                
    def send_message(self):
        if self.client and self.message_entry.get():
            self.client.send(self.message_entry.get())
            self.message_entry.delete(0, tk.END)
                    
    def disconnect(self):
        if self.client:
            self.client.disconnect()
            
        if self.db_manager and self.session_id:
            self.db_manager.end_session(self.session_id)
            self.session_id = None
            
        self.update_ui_state(False, is_server=False)
