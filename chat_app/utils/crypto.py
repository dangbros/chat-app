# chat_app/utils/crypto.py
"""
XOR Encryption utilities for secure message transfer
"""

class XorCipher:
    """Simple XOR cipher for message encryption/decryption"""
    
    def __init__(self, key: str = "default_key_123"):
        self.key = key
        self.key_bytes = key.encode('utf-8')
        
    def set_key(self, key: str) -> None:
        """Update encryption key"""
        self.key = key
        self.key_bytes = key.encode('utf-8')
        
    def encrypt(self, plaintext: str) -> bytes:
        """
        Encrypt string using XOR with key
        Returns base64 encoded bytes for safe transmission
        """
        plaintext_bytes = plaintext.encode('utf-8')
        encrypted = bytearray()
        
        for i, byte in enumerate(plaintext_bytes):
            key_byte = self.key_bytes[i % len(self.key_bytes)]
            encrypted.append(byte ^ key_byte)
            
        # Convert to base64 for safe string transmission
        import base64
        return base64.b64encode(bytes(encrypted))
    
    def decrypt(self, encrypted_b64: bytes) -> str:
        """
        Decrypt base64 encoded XOR encrypted message
        """
        import base64
        
        try:
            encrypted = base64.b64decode(encrypted_b64)
            decrypted = bytearray()
            
            for i, byte in enumerate(encrypted):
                key_byte = self.key_bytes[i % len(self.key_bytes)]
                decrypted.append(byte ^ key_byte)
                
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
        
    def encrypt_bytes(self, data: bytes) -> bytes:
        """Raw XOR encryption without base64"""
        encrypted = bytearray()
        for i, byte in enumerate(data):
            key_byte = self.key_bytes[i % len(self.key_bytes)]
            encrypted.append(byte ^ key_byte)
        return bytes(encrypted)
    
    def decrypt_bytes(self, data: bytes) -> bytes:
        """Raw XOR decryption"""
        return self.encrypt_bytes(data)  # XOR is symmetric


# Global cipher instance (can be configured)
_default_cipher = XorCipher()

def set_global_key(key: str) -> None:
    """Set global encryption key"""
    _default_cipher.set_key(key)
    
def get_cipher() -> XorCipher:
    """Get default cipher instance"""
    return _default_cipher