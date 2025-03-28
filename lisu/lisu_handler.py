from typing import Dict, List, Optional
from .device_manager import DeviceManager
from .command_handler import CommandHandler
from .udp_manager import UDPManager

class LisuManager:
    def __init__(self):
        self.device_manager = DeviceManager()
        self.command_handler = CommandHandler()
        self.udp_manager = UDPManager()
        self.current_device = None
        
    def get_available_devices(self) -> List[Dict]:
        """Get list of available devices"""
        return self.device_manager.detect_devices()
        
    def connect_device(self, device_name: str) -> bool:
        """Connect to a device"""
        if self.device_manager.connect_device(device_name):
            self.current_device = device_name
            return True
        return False
        
    def disconnect_device(self):
        """Disconnect from current device"""
        self.device_manager.disconnect_device()
        self.current_device = None
        
    def get_device_status(self) -> Dict:
        """Get current device status"""
        return self.device_manager.get_device_status()
        
    def send_command(self, command_type: str, values: Dict[str, float]) -> bool:
        """Send a command to the current device"""
        if not self.current_device:
            raise RuntimeError("No device connected")
            
        # Get device type from device manager
        device_info = self.device_manager.device_config["input_devices"][self.current_device]
        device_type = device_info["type"]
        
        # Format and send command
        if command_type == "rotation":
            success = self.command_handler.send_rotation_command(
                device_type,
                values.get('x', 0.0),
                values.get('y', 0.0),
                values.get('z', 0.0)
            )
        else:
            success = self.command_handler.send_command(
                device_type,
                command_type,
                values.get('value', 0.0)
            )
            
        if success:
            # Send command via UDP
            return self.udp_manager.send_message(command_type)
        return False
        
    def set_udp_target(self, ip: str, port: int):
        """Set UDP target address and port"""
        self.udp_manager.set_target(ip, port)
        
    def get_udp_target(self) -> Dict[str, str]:
        """Get current UDP target"""
        return {
            "ip": self.udp_manager.target_ip,
            "port": str(self.udp_manager.target_port)
        } 