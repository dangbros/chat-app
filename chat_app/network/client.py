# chat_app/network/client.py
import socket
import threading
from typing import Optional
from ..utils.crypto import XorCipher, get_cipher

class ChatClient:
    """Client network handler with XOR encryption"""
    
    def __init__(self, host: str, port: int, logger, on_connect, on_disconnect, on_receive,
                 cipher: Optional[XorCipher] = None):
        self.host = host
        self.port = port
        self.logger = logger
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_receive = on_receive
        
        self.cipher = cipher or get_cipher()
        self.client_socket: Optional[socket.socket] = None
        self.receive_thread: Optional[threading.Thread] = None
        self.running = False
        
    def connect(self) -> bool:
        """Connect to server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            
            self.running = True
            self.logger.output(f"Connected to server at {self.host}:{self.port} (XOR encryption enabled)", "system", "System")
            
            # Notify GUI
            self.on_connect()
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
            return True
            
        except Exception as e:
            self.logger.output(f"Connection failed: {e}", "error", "System")
            return False
            
    def _receive_messages(self) -> None:
        """Receive and decrypt messages from server"""
        try:
            while self.running:
                data = self.client_socket.recv(4096)  # Larger buffer for base64
                if not data:
                    self.logger.output("Server disconnected", "system", "System")
                    self.on_disconnect()
                    break
                    
                # Decrypt received data
                try:
                    decrypted = self.cipher.decrypt(data)
                    self.logger.output(f"[ENCRYPTED] {data[:50]}... -> {decrypted}", "received", "Server")
                    self.on_receive(decrypted)
                except Exception:
                    # Fallback: treat as plain text
                    decrypted = data.decode('utf-8')
                    self.logger.output(f"[PLAIN] {decrypted}", "received", "Server")
                    self.on_receive(decrypted)
                    
        except Exception as e:
            if self.running:
                self.logger.output(f"Receive error: {e}", "error", "System")
                self.on_disconnect()
                
    def send(self, message: str) -> bool:
        """Send encrypted message to server"""
        if self.client_socket and self.running:
            try:
                # Encrypt message
                encrypted = self.cipher.encrypt(message)
                self.client_socket.sendall(encrypted)
                self.logger.output(f"[ENCRYPTED] {message} -> {encrypted[:50]}...", "sent", "You")
                return True
            except Exception as e:
                self.logger.output(f"Send failed: {e}", "error", "System")
                return False
        return False
        
    def disconnect(self) -> None:
        """Disconnect from server"""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        self.logger.output("Disconnected from server", "system", "System")
        self.on_disconnect()
        
    def set_encryption_key(self, key: str) -> None:
        """Update encryption key"""
        self.cipher.set_key(key)
        self.logger.output(f"Encryption key updated", "system", "System")
