# chat_app/network/server.py
import socket
import threading
from typing import Optional, Callable
from ..utils.crypto import XorCipher, get_cipher

class ChatServer:
    """Server network handler with XOR encryption"""
    
    def __init__(self, host: str, port: int, logger, on_connect, on_disconnect, on_receive, 
                 cipher: Optional[XorCipher] = None):
        self.host = host
        self.port = port
        self.logger = logger
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_receive = on_receive
        
        self.cipher = cipher or get_cipher()
        self.server_socket: Optional[socket.socket] = None
        self.client_conn: Optional[socket.socket] = None
        self.client_addr = None
        self.running = False
        
    def start(self) -> bool:
        """Start the server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            
            self.running = True
            self.logger.output(f"Server started on {self.host}:{self.port} (XOR encryption enabled)", "system", "System")
            
            # Start accept thread
            accept_thread = threading.Thread(target=self._accept_clients, daemon=True)
            accept_thread.start()
            return True
            
        except Exception as e:
            self.logger.output(f"Failed to start server: {e}", "error", "System")
            return False
            
    def _accept_clients(self) -> None:
        """Accept incoming connections"""
        try:
            self.server_socket.settimeout(1.0)
            while self.running:
                try:
                    conn, addr = self.server_socket.accept()
                    self.client_conn = conn
                    self.client_addr = addr
                    self.logger.output(f"Client connected from {addr[0]}:{addr[1]}", "system", "System")
                    
                    # Notify GUI
                    self.on_connect(addr)
                    
                    # Handle client
                    self._handle_client(conn, addr)
                    break
                except socket.timeout:
                    continue
        except Exception as e:
            if self.running:
                self.logger.output(f"Accept error: {e}", "error", "System")
                
    def _handle_client(self, conn: socket.socket, addr) -> None:
        """Handle client communication with decryption"""
        try:
            while self.running:
                data = conn.recv(4096)  # Larger buffer for base64
                if not data:
                    self.logger.output("Client disconnected", "system", "System")
                    break
                    
                # Decrypt received data
                try:
                    decrypted = self.cipher.decrypt(data)
                    self.logger.output(f"[ENCRYPTED] {data[:50]}... -> {decrypted}", "received", f"Client({addr[0]})")
                except Exception as e:
                    # Fallback: treat as plain text for backward compatibility
                    decrypted = data.decode('utf-8')
                    self.logger.output(f"[PLAIN] {decrypted}", "received", f"Client({addr[0]})")
                    
        except Exception as e:
            if self.running:
                self.logger.output(f"Client error: {e}", "error", "System")
        finally:
            conn.close()
            self.client_conn = None
            self.on_disconnect()
            
    def send(self, message: str) -> bool:
        """Send encrypted message to client"""
        if self.client_conn and self.running:
            try:
                # Encrypt message
                encrypted = self.cipher.encrypt(message)
                self.client_conn.sendall(encrypted)
                self.logger.output(f"[ENCRYPTED] {message} -> {encrypted[:50]}...", "sent", "You")
                return True
            except Exception as e:
                self.logger.output(f"Send failed: {e}", "error", "System")
                return False
        return False
        
    def stop(self) -> None:
        """Stop the server"""
        self.running = False
        if self.client_conn:
            try:
                self.client_conn.close()
            except:
                pass
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.logger.output("Server stopped", "system", "System")
        
    def set_encryption_key(self, key: str) -> None:
        """Update encryption key"""
        self.cipher.set_key(key)
        self.logger.output(f"Encryption key updated", "system", "System")