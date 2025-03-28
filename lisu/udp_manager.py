import socket
from typing import Optional
import json
from pathlib import Path

class UDPManager:
    def __init__(self):
        self.socket = None
        self.target_ip = "127.0.0.1"
        self.target_port = 7755
        self.load_config()
        
    def load_config(self):
        """Load UDP configuration from JSON file"""
        config_path = Path("data/config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                udp_config = config.get("udp", {})
                self.target_ip = udp_config.get("ip", "127.0.0.1")
                self.target_port = udp_config.get("port", 7755)
        else:
            # Create default config
            config = {
                "udp": {
                    "ip": "127.0.0.1",
                    "port": 7755
                }
            }
            # Create data directory if it doesn't exist
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
                
    def connect(self) -> bool:
        """Create UDP socket"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return True
        except Exception as e:
            print(f"Error creating UDP socket: {e}")
            return False
            
    def disconnect(self):
        """Close UDP socket"""
        if self.socket:
            self.socket.close()
            self.socket = None
            
    def send_message(self, message: str) -> bool:
        """Send message via UDP"""
        if not self.socket:
            if not self.connect():
                return False
                
        try:
            self.socket.sendto(message.encode(), (self.target_ip, self.target_port))
            return True
        except Exception as e:
            print(f"Error sending UDP message: {e}")
            return False
            
    def set_target(self, ip: str, port: int):
        """Set UDP target address and port"""
        self.target_ip = ip
        self.target_port = port
        
        # Update config file
        config_path = Path("data/config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                config["udp"] = {
                    "ip": ip,
                    "port": port
                }
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=4) 