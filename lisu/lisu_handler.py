from typing import Dict, Optional
import json
import os
from pathlib import Path

class LisuManager:
    def __init__(self):
        self.config_path = Path("data/visualisation_config.json")
        self.current_device = None
        self.device_config = None
        self.load_config()
        
    def load_config(self):
        """Load the configuration file if it exists, otherwise create default config."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.device_config = json.load(f)
        else:
            self.device_config = {
                "input_devices": {
                    "Bluetooth_mouse": {
                        "vid": "046d",
                        "pid": "b03a",
                        "type": "mouse"
                    },
                    "SpaceMouse": {
                        "vid": "256f",
                        "pid": "c635",
                        "type": "3dconnexion"
                    }
                },
                "actuation": {
                    "commands": {
                        "mouse": "addrotation %.3f 0.0 0.0 %s",
                        "3dconnexion": "addrotation %.3f %.3f %.3f %s"
                    }
                },
                "visualisation": {
                    "render_options": {
                        "visualisations": {
                            "Drishti-v2.6.4": {
                                "udp_ip": "127.0.0.1",
                                "udp_port": 7755
                            }
                        }
                    }
                }
            }
            # Create data directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.device_config, f, indent=4)
    
    def connect_device(self, device_name: str) -> bool:
        """Connect to a specific device."""
        if device_name not in self.device_config["input_devices"]:
            raise ValueError(f"Device {device_name} not found in configuration")
            
        self.current_device = device_name
        device_info = self.device_config["input_devices"][device_name]
        
        # Here we would integrate with the original LISU framework
        # For now, we'll just return True to indicate successful connection
        return True
    
    def disconnect_device(self):
        """Disconnect from the current device."""
        if self.current_device:
            # Here we would integrate with the original LISU framework
            # to properly disconnect the device
            self.current_device = None
    
    def send_command(self, command_type: str, values: Dict[str, float]) -> bool:
        """Send a command to the connected device."""
        if not self.current_device:
            raise RuntimeError("No device connected")
            
        device_info = self.device_config["input_devices"][self.current_device]
        command_template = self.device_config["actuation"]["commands"][device_info["type"]]
        
        # Format the command with the provided values
        command = command_template % (
            values.get('x', 0.0),
            values.get('y', 0.0),
            values.get('z', 0.0),
            "1"  # Default duration
        )
        
        # Here we would integrate with the original LISU framework
        # to send the command via UDP
        print(f"Sending command: {command}")
        return True
    
    def get_available_devices(self) -> list:
        """Get a list of available devices from the configuration."""
        return list(self.device_config["input_devices"].keys()) 