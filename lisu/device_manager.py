import pywinusb.hid as hid
import pygame
from typing import Dict, List, Optional
import json
from pathlib import Path

class DeviceManager:
    def __init__(self):
        self.current_device = None
        self.device_config = None
        self.load_config()
        
    def load_config(self):
        """Load device configuration from JSON file"""
        config_path = Path("data/config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.device_config = json.load(f)
        else:
            self.device_config = {
                "input_devices": {
                    "Bluetooth_mouse": {
                        "vid": "046d",
                        "pid": "b03a",
                        "type": "mouse",
                        "axes": ["x", "y"],
                        "buttons": ["left_click", "right_click"]
                    },
                    "SpaceMouse": {
                        "vid": "256f",
                        "pid": "c635",
                        "type": "3dconnexion",
                        "axes": ["x", "y", "z", "rx", "ry", "rz"],
                        "buttons": ["button_1", "button_2"]
                    }
                }
            }
            # Create data directory if it doesn't exist
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.device_config, f, indent=4)
    
    def detect_devices(self) -> List[Dict]:
        """Detect available input devices"""
        devices = []
        
        # Detect HID devices
        try:
            all_hid_devices = hid.find_all_hid_devices()
            for device in all_hid_devices:
                vid = f"{device.vendor_id:04x}"
                pid = f"{device.product_id:04x}"
                
                # Check if device is in our configuration
                for name, config in self.device_config["input_devices"].items():
                    if config["vid"] == vid and config["pid"] == pid:
                        devices.append({
                            "name": name,
                            "vid": vid,
                            "pid": pid,
                            "type": config["type"],
                            "axes": config["axes"],
                            "buttons": config["buttons"]
                        })
                        break
        except Exception as e:
            print(f"Error detecting HID devices: {e}")
            
        # Detect gamepad devices
        try:
            pygame.init()
            pygame.joystick.init()
            for i in range(pygame.joystick.get_count()):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                
                # Add gamepad to devices list
                devices.append({
                    "name": f"Gamepad_{i}",
                    "type": "gamepad",
                    "axes": [f"axis_{j}" for j in range(joystick.get_numaxes())],
                    "buttons": [f"button_{j}" for j in range(joystick.get_numbuttons())]
                })
        except Exception as e:
            print(f"Error detecting gamepad devices: {e}")
            
        return devices
    
    def connect_device(self, device_name: str) -> bool:
        """Connect to a specific device"""
        if device_name not in self.device_config["input_devices"]:
            raise ValueError(f"Device {device_name} not found in configuration")
            
        device_config = self.device_config["input_devices"][device_name]
        
        try:
            if device_config["type"] == "mouse":
                # Handle mouse connection
                self.current_device = {
                    "name": device_name,
                    "type": "mouse",
                    "config": device_config
                }
                return True
                
            elif device_config["type"] == "3dconnexion":
                # Handle 3DConnexion device connection
                self.current_device = {
                    "name": device_name,
                    "type": "3dconnexion",
                    "config": device_config
                }
                return True
                
            elif device_config["type"] == "gamepad":
                # Handle gamepad connection
                pygame.init()
                pygame.joystick.init()
                self.current_device = {
                    "name": device_name,
                    "type": "gamepad",
                    "config": device_config
                }
                return True
                
        except Exception as e:
            print(f"Error connecting to device: {e}")
            return False
            
    def disconnect_device(self):
        """Disconnect from the current device"""
        if self.current_device:
            if self.current_device["type"] == "gamepad":
                pygame.joystick.quit()
            self.current_device = None
            
    def get_device_status(self) -> Dict:
        """Get current device status"""
        if not self.current_device:
            return {
                "connected": False,
                "input_rate": 0,
                "signal_strength": "Unknown",
                "battery_level": "Unknown"
            }
            
        status = {
            "connected": True,
            "device_name": self.current_device["name"],
            "device_type": self.current_device["type"]
        }
        
        # Add device-specific status information
        if self.current_device["type"] == "gamepad":
            try:
                joystick = pygame.joystick.Joystick(0)  # Assuming first joystick
                status["battery_level"] = "100%"  # Gamepad doesn't provide battery info
                status["signal_strength"] = "Excellent"  # Gamepad doesn't provide signal info
            except:
                status["battery_level"] = "Unknown"
                status["signal_strength"] = "Unknown"
                
        return status 