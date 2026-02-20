# chat_app/gui/history_viewer.py
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk


class HistoryViewer:
    """Window to view chat history"""

    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Archive Terminal")
        self.window.geometry("800x600")
        self.window.configure(bg="#050b05")
        self._title_glow_index = 0
        self._title_glow = ["#39d939", "#66ff66", "#98ff98", "#66ff66"]

        self.colors = {
            'bg': "#050b05",
            'secondary': "#081408",
            'accent': "#0f2d0f",
            'highlight': "#25d225",
            'text': "#7CFF7C",
            'muted': "#2f7f2f",
            'success': "#66ff66",
            'received': "#98ff98",
            'sent': "#25d225"
        }

        self.create_widgets()
        self.load_sessions()
        self.animate_header()

    def create_widgets(self):
        style = ttk.Style(self.window)
        style.theme_use('clam')
        style.configure("Treeview",
                        background=self.colors['secondary'],
                        foreground=self.colors['text'],
                        fieldbackground=self.colors['secondary'],
                        borderwidth=0,
                        rowheight=24)
        style.configure("Treeview.Heading",
                        background=self.colors['accent'],
                        foreground=self.colors['success'],
                        relief="flat")
        style.map("Treeview", background=[('selected', '#1f541f')], foreground=[('selected', '#98ff98')])

        # Top frame with search
        top_frame = tk.Frame(self.window, bg=self.colors['bg'])
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        self.title_label = tk.Label(top_frame, text="ARCHIVE QUERY>", bg=self.colors['bg'],
                                    fg=self.colors['highlight'], font=('Courier', 11, 'bold'))
        self.title_label.pack(side=tk.LEFT, padx=(0, 8))

        self.search_entry = tk.Entry(top_frame, width=30,
                                     bg=self.colors['secondary'],
                                     fg=self.colors['text'],
                                     insertbackground=self.colors['text'],
                                     relief=tk.FLAT,
                                     font=('Courier', 10))
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10), ipady=2)
        self.search_entry.bind('<Return>', lambda e: self.search())

        tk.Button(top_frame, text="SCAN",
                  bg=self.colors['accent'],
                  fg=self.colors['text'],
                  activebackground="#1f541f",
                  relief=tk.FLAT,
                  font=('Courier', 10, 'bold'),
                  command=self.search).pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="RELOAD",
                  bg=self.colors['success'],
                  fg=self.colors['bg'],
                  activebackground="#98ff98",
                  relief=tk.FLAT,
                  font=('Courier', 10, 'bold'),
                  command=self.load_sessions).pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="PURGE",
                  bg="#1f541f",
                  fg=self.colors['text'],
                  activebackground="#ff6b6b",
                  relief=tk.FLAT,
                  font=('Courier', 10, 'bold'),
                  command=self.delete_selected).pack(side=tk.RIGHT, padx=5)

        # Paned window for split view
        paned = tk.PanedWindow(self.window, orient=tk.HORIZONTAL, bg=self.colors['bg'])
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Sessions list (left side)
        left_frame = tk.Frame(paned, bg=self.colors['bg'])
        paned.add(left_frame, width=250)

        tk.Label(left_frame, text="SESSION LOGS",
                 bg=self.colors['bg'], fg=self.colors['text'],
                 font=('Courier', 12, 'bold')).pack(pady=(0, 5))

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

        tk.Label(right_frame, text="MESSAGE DUMP",
                 bg=self.colors['bg'], fg=self.colors['text'],
                 font=('Courier', 12, 'bold')).pack(pady=(0, 5))

        self.chat_display = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            font=('Courier', 10),
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
                           ("error", "#ff6b6b")]:
            self.chat_display.tag_configure(tag, foreground=color)

    def animate_header(self):
        self._title_glow_index = (self._title_glow_index + 1) % len(self._title_glow)
        self.title_label.config(fg=self._title_glow[self._title_glow_index])
        self.window.after(380, self.animate_header)

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
                    self.chat_display.insert(tk.END, f"<< RX {sender}: ", "received")
                    self.chat_display.insert(tk.END, f"{message}\n", "received")
                elif msg_type == "sent":
                    self.chat_display.insert(tk.END, f">> TX {sender}: ", "sent")
                    self.chat_display.insert(tk.END, f"{message}\n", "sent")
                else:
                    self.chat_display.insert(tk.END, f":: {message}\n", "system")

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
