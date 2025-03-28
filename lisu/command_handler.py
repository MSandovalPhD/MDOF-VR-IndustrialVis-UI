from typing import Dict, Optional
import json
from pathlib import Path

class CommandHandler:
    def __init__(self):
        self.command_config = None
        self.load_config()
        
    def load_config(self):
        """Load command configuration from JSON file"""
        config_path = Path("data/config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.command_config = config.get("commands", {})
        else:
            self.command_config = {
                "commands": {
                    "mouse": {
                        "x_axis": "addrotation %.3f 0.0 0.0 %s",
                        "y_axis": "addrotation 0.0 %.3f 0.0 %s",
                        "z_axis": "addrotation 0.0 0.0 %.3f %s"
                    },
                    "3dconnexion": {
                        "x_axis": "addrotation %.3f 0.0 0.0 %s",
                        "y_axis": "addrotation 0.0 %.3f 0.0 %s",
                        "z_axis": "addrotation 0.0 0.0 %.3f %s",
                        "rx_axis": "addrotation %.3f 0.0 0.0 %s",
                        "ry_axis": "addrotation 0.0 %.3f 0.0 %s",
                        "rz_axis": "addrotation 0.0 0.0 %.3f %s"
                    },
                    "gamepad": {
                        "axis_0": "addrotation %.3f 0.0 0.0 %s",
                        "axis_1": "addrotation 0.0 %.3f 0.0 %s",
                        "axis_2": "addrotation 0.0 0.0 %.3f %s"
                    }
                }
            }
            # Create data directory if it doesn't exist
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.command_config, f, indent=4)
                
    def format_command(self, device_type: str, axis: str, value: float, duration: float = 1.0) -> str:
        """Format a command string based on device type and axis"""
        if device_type not in self.command_config["commands"]:
            raise ValueError(f"Unknown device type: {device_type}")
            
        device_commands = self.command_config["commands"][device_type]
        if axis not in device_commands:
            raise ValueError(f"Unknown axis for device type {device_type}: {axis}")
            
        command_template = device_commands[axis]
        return command_template % (value, duration)
        
    def process_input(self, device_type: str, axis: str, raw_value: float) -> float:
        """Process raw input value based on device type and axis"""
        # Apply any necessary transformations or scaling
        # For now, just normalize the value to [-1, 1]
        return max(min(raw_value, 1.0), -1.0)
        
    def send_command(self, device_type: str, axis: str, value: float, duration: float = 1.0) -> bool:
        """Send a command to the device"""
        try:
            # Process the input value
            processed_value = self.process_input(device_type, axis, value)
            
            # Format the command
            command = self.format_command(device_type, axis, processed_value, duration)
            
            # Here we would send the command via UDP
            # For now, just print it
            print(f"Sending command: {command}")
            return True
            
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
            
    def send_rotation_command(self, device_type: str, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> bool:
        """Send a rotation command with x, y, z values"""
        try:
            # Process each axis value
            x = self.process_input(device_type, "x_axis", x)
            y = self.process_input(device_type, "y_axis", y)
            z = self.process_input(device_type, "z_axis", z)
            
            # Format the command
            command = f"addrotation {x:.3f} {y:.3f} {z:.3f} 1.0"
            
            # Here we would send the command via UDP
            # For now, just print it
            print(f"Sending rotation command: {command}")
            return True
            
        except Exception as e:
            print(f"Error sending rotation command: {e}")
            return False 