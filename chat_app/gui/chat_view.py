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
        self.retro_font = "OCR A Extended"
        self.retro_fallback = "Courier New"
        self._status_anim_state = False
        self._header_pulse_index = 0
        self._header_pulse_colors = ["#0d1f0d", "#113311", "#153f15", "#113311"]

        # Fallout/Matrix retro terminal palette
        self.colors = {
            'bg': "#050b05",
            'secondary': "#081408",
            'accent': "#0f2d0f",
            'highlight': "#25d225",
            'text': "#7CFF7C",
            'muted': "#2f7f2f",
            'success': "#66ff66",
            'received': "#98ff98",
            'sent': "#39d939",
            'warn': "#c4ff6f",
            'danger': "#ff6b6b",
        }

        self.root.configure(bg=self.colors['bg'])
        title_mode = "SERVER NODE" if self.is_server else "CLIENT NODE"
        self.root.title(f"VAULT-TEC DATALINK // {title_mode}")
        self.root.geometry("1080x720")
        self.root.minsize(980, 660)
        self.root.option_add("*Font", f"{self.retro_fallback} 12")

        self.create_widgets()
        self.process_queue()
        self.animate_status()
        self.pulse_header()

    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        self.header = tk.Frame(main_frame, bg=self.colors['secondary'], height=60, highlightthickness=1,
                               highlightbackground=self.colors['highlight'])
        self.header.pack(fill=tk.X, pady=(0, 15))
        self.header.pack_propagate(False)

        title_text = "[ 🛰 SERVER TERMINAL ]" if self.is_server else "[ 📻 CLIENT TERMINAL ]"
        self.title_label = tk.Label(
            self.header,
            text=title_text,
            bg=self.colors['secondary'],
            fg=self.colors['highlight'],
            font=(self.retro_font, 16, 'bold')
        )
        self.title_label.pack(side=tk.LEFT, padx=20, pady=10)

        self.status_label = tk.Label(
            self.header,
            text="◉ OFFLINE",
            bg=self.colors['secondary'],
            fg=self.colors['muted'],
            font=(self.retro_fallback, 12, 'bold')
        )
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=10)

        # Connection frame
        conn_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        conn_frame.pack(fill=tk.X, pady=(0, 15))

        # Host input
        tk.Label(conn_frame, text="🌐 HOST>", bg=self.colors['bg'],
                 fg=self.colors['text'], font=(self.retro_fallback, 12, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.host_entry = tk.Entry(conn_frame, width=15,
                                   bg=self.colors['secondary'],
                                   fg=self.colors['text'],
                                   insertbackground=self.colors['text'],
                                   relief=tk.FLAT,
                                   highlightthickness=1,
                                   highlightbackground=self.colors['accent'],
                                   highlightcolor=self.colors['highlight'],
                                   font=(self.retro_fallback, 12))
        self.host_entry.pack(side=tk.LEFT, padx=(0, 15), ipady=2)
        self.host_entry.insert(0, "127.0.0.1")

        # Port input
        tk.Label(conn_frame, text="⚙ PORT>", bg=self.colors['bg'],
                 fg=self.colors['text'], font=(self.retro_fallback, 12, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.port_entry = tk.Entry(conn_frame, width=8,
                                   bg=self.colors['secondary'],
                                   fg=self.colors['text'],
                                   insertbackground=self.colors['text'],
                                   relief=tk.FLAT,
                                   highlightthickness=1,
                                   highlightbackground=self.colors['accent'],
                                   highlightcolor=self.colors['highlight'],
                                   font=(self.retro_fallback, 12))
        self.port_entry.pack(side=tk.LEFT, padx=(0, 15), ipady=2)
        self.port_entry.insert(0, "65432")

        # Action button
        action_text = "🛰 BOOT SERVER" if self.is_server else "🔗 LINK"
        self.action_btn = tk.Button(conn_frame, text=action_text,
                                    bg=self.colors['accent'],
                                    activebackground="#1f541f",
                                    fg=self.colors['highlight'],
                                    activeforeground=self.colors['success'],
                                    font=(self.retro_font, 12, 'bold'),
                                    relief=tk.FLAT,
                                    cursor="hand2",
                                    command=self.toggle_connection)
        self.action_btn.pack(side=tk.LEFT, padx=10, ipady=2, ipadx=6)

        # Chat display
        chat_container = tk.Frame(main_frame, bg=self.colors['secondary'], bd=1, relief=tk.FLAT,
                                  highlightthickness=1, highlightbackground=self.colors['accent'])
        chat_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            font=(self.retro_fallback, 13),
            padx=15,
            pady=15,
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Configure tags for styling
        self.chat_display.tag_configure("timestamp", foreground=self.colors['muted'], font=(self.retro_fallback, 10))
        self.chat_display.tag_configure("received", foreground=self.colors['received'], font=(self.retro_fallback, 13, 'bold'))
        self.chat_display.tag_configure("sent", foreground=self.colors['sent'], font=(self.retro_fallback, 13, 'bold'))
        self.chat_display.tag_configure("system", foreground=self.colors['success'], font=(self.retro_fallback, 12, 'italic'))
        self.chat_display.tag_configure("error", foreground=self.colors['danger'], font=(self.retro_fallback, 12, 'bold'))

        # Input area
        input_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        input_frame.pack(fill=tk.X)

        self.message_entry = tk.Entry(input_frame,
                                      bg=self.colors['secondary'],
                                      fg=self.colors['text'],
                                      insertbackground=self.colors['text'],
                                      relief=tk.FLAT,
                                      highlightthickness=1,
                                      highlightbackground=self.colors['accent'],
                                      highlightcolor=self.colors['highlight'],
                                      font=(self.retro_fallback, 13),
                                      state=tk.DISABLED)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=8)

        self.send_btn = tk.Button(input_frame, text="📨 TRANSMIT >>",
                                  bg=self.colors['accent'],
                                  activebackground="#1f541f",
                                  fg=self.colors['highlight'],
                                  activeforeground=self.colors['success'],
                                  font=(self.retro_font, 12, 'bold'),
                                  relief=tk.FLAT,
                                  cursor="hand2",
                                  state=tk.DISABLED,
                                  command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT, ipadx=20, ipady=5)

    def animate_status(self):
        """Blink status indicator for retro terminal feel."""
        connected = self.message_entry.cget("state") == tk.NORMAL
        if connected:
            self._status_anim_state = not self._status_anim_state
            fg_color = self.colors['success'] if self._status_anim_state else self.colors['muted']
            current = self.status_label.cget("text").upper()
            if "ONLINE" in current or "LISTEN" in current or "CONNECTED" in current:
                self.status_label.config(fg=fg_color)
        self.root.after(450, self.animate_status)

    def pulse_header(self):
        """Subtle pulse animation on the header background."""
        self._header_pulse_index = (self._header_pulse_index + 1) % len(self._header_pulse_colors)
        color = self._header_pulse_colors[self._header_pulse_index]
        self.header.configure(bg=color)
        self.title_label.configure(bg=color)
        self.status_label.configure(bg=color)
        self.root.after(380, self.pulse_header)

    def add_message(self, text: str, msg_type: str = "system") -> None:
        """Add message to GUI display"""
        timestamp = time.strftime("%H:%M:%S")
        self.chat_display.config(state=tk.NORMAL)

        if msg_type == "received":
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.chat_display.insert(tk.END, "<< RX ", "received")
            self.chat_display.insert(tk.END, f"{text}\n", "received")
        elif msg_type == "sent":
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.chat_display.insert(tk.END, ">> TX ", "sent")
            self.chat_display.insert(tk.END, f"{text}\n", "sent")
        elif msg_type == "error":
            self.chat_display.insert(tk.END, f"[{timestamp}] !! ", "error")
            self.chat_display.insert(tk.END, f"{text}\n", "error")
        else:
            self.chat_display.insert(tk.END, f"[{timestamp}] :: ", "system")
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
            self.action_btn.config(text="⛔ SHUTDOWN" if is_server else "❌ UNLINK", bg="#1f541f")
            self.host_entry.config(state=tk.DISABLED)
            self.port_entry.config(state=tk.DISABLED)
            if is_server:
                self.status_label.config(text="◉ LISTENING", fg=self.colors['warn'])
            else:
                self.status_label.config(text="◉ ONLINE", fg=self.colors['success'])
            self.message_entry.config(state=tk.NORMAL)
            self.send_btn.config(state=tk.NORMAL)
        else:
            self.action_btn.config(text="🛰 BOOT SERVER" if is_server else "🔗 LINK", bg=self.colors['accent'])
            self.host_entry.config(state=tk.NORMAL)
            self.port_entry.config(state=tk.NORMAL)
            self.status_label.config(text="◉ OFFLINE", fg=self.colors['muted'])
            self.message_entry.config(state=tk.DISABLED)
            self.send_btn.config(state=tk.DISABLED)
