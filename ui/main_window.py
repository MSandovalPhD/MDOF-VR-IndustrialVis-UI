from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QStatusBar,
                             QGroupBox, QGridLayout, QSpacerItem, QSizePolicy,
                             QLineEdit, QTextEdit)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPen, QColor, QPainterPath
import qtawesome as qta
import darkdetect
from pathlib import Path
import socket
import json
from datetime import datetime
import pygame

class MainWindow(QMainWindow):
    def __init__(self, lisu_manager):
        super().__init__()
        self.lisu = lisu_manager
        
        # Initialize pygame for gamepad support
        pygame.init()
        pygame.joystick.init()
        
        # Gamepad state and calibration
        self.gamepad = None
        self.is_reading_input = False
        self.input_timer = QTimer()
        self.input_timer.timeout.connect(self.read_gamepad_input)
        self.x_offset = 0.0
        self.y_offset = 0.0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Load configuration first
        try:
            with open("data/config.json", "r") as f:
                self.config = json.load(f)
        except Exception as e:
            self.config = {"udp": {"ip": "127.0.0.1", "port": 7755}}
            print(f"Error loading config: {str(e)}")

        # Initialize UDP socket
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.settimeout(0.1)  # 100ms timeout for non-blocking operations

        # Set window properties
        self.setWindowTitle("LISU Framework Control Panel")
        self.setMinimumSize(1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create header container
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Logo container (25% width)
        logo_container = QWidget()
        logo_container.setFixedWidth(200)
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.setContentsMargins(10, 10, 10, 10)
        
        # Logo
        logo_label = QLabel()
        logo_label.setFixedSize(75, 75)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("QLabel { background-color: transparent; }")
        
        # Load logo from resources
        logo_svg = Path("resources/logo.svg")
        logo_png = Path("resources/Logo.png")  # Note the capital L
        
        if logo_png.exists():
            pixmap = QPixmap(str(logo_png))
            scaled_pixmap = pixmap.scaled(
                75, 75,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(scaled_pixmap)
        elif logo_svg.exists():
            try:
                pixmap = QPixmap(str(logo_svg))
                scaled_pixmap = pixmap.scaled(
                    75, 75,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                logo_label.setPixmap(scaled_pixmap)
            except:
                self.statusBar.showMessage("Error loading SVG logo")
                return
        else:
            self.statusBar.showMessage("Logo file not found")
            return
            
        logo_layout.addWidget(logo_label)
        
        # Welcome message container (75% width)
        welcome_container = QWidget()
        welcome_layout = QHBoxLayout(welcome_container)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        welcome_layout.setContentsMargins(20, 10, 10, 10)
        
        # Welcome message
        welcome_text = QLabel(
            "Welcome to the Layered Interaction System for User-Modes (LISU) \n"
            "Control VR visualisations, manipulate 3D models and navigate virtual environments"
        )
        welcome_text.setWordWrap(False)  # Prevent text wrapping
        welcome_font = QFont()
        welcome_font.setPointSize(11)
        welcome_font.setBold(True)
        welcome_text.setFont(welcome_font)
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        welcome_layout.addWidget(welcome_text)
        
        # Add containers to header layout
        header_layout.addWidget(logo_container)
        header_layout.addWidget(welcome_container, 1)  # 1 is stretch factor
        header_layout.setSpacing(0)  # Remove spacing between containers
        header_layout.setContentsMargins(0, 0, 0, 0)  # Remove container margins
        
        # Add header to main layout
        main_layout.addWidget(header_container)
        main_layout.addSpacing(10)
        
        
        # Add small spacing after header
        main_layout.addSpacing(10)
        
        # Device Selection and Configuration
        device_group = QGroupBox("Device Selection and Configuration")
        device_layout = QGridLayout()
        
        # First row: Device Selection and Visualisation Target
        device_layout.addWidget(QLabel("Select Device:"), 0, 0)
        self.device_type_combo = QComboBox()
        self.device_type_combo.addItems(["Gamepad_0", "Bluetooth_mouse", "SpaceMouse"])
        device_layout.addWidget(self.device_type_combo, 0, 1)
        
        device_layout.addWidget(QLabel("Visualisation Target:"), 0, 2)
        self.vis_combo = QComboBox()
        self.vis_combo.addItems(self.config.get("visualisations", {}).get("available_targets", []))
        self.vis_combo.currentTextChanged.connect(self.on_visualisation_changed)
        device_layout.addWidget(self.vis_combo, 0, 3)
        
        # Second row: Command Type
        device_layout.addWidget(QLabel("Command Type:"), 1, 0)
        self.cmd_combo = QComboBox()
        self.cmd_combo.addItems(self.config.get("commands", {}).get("available_commands", []))
        self.cmd_combo.currentTextChanged.connect(self.on_command_changed)
        device_layout.addWidget(self.cmd_combo, 1, 1, 1, 3)  # Span 3 columns
        
        # Third row: Movement Parameters
        device_layout.addWidget(QLabel("Movement Parameters:"), 2, 0, 1, 4)  # Span all columns
        
        # Fourth row: Rotation Angle and Movement Step
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(QLabel("Rotation Angle (°):"))
        
        rotation_minus_btn = QPushButton("-")
        rotation_minus_btn.setIcon(qta.icon('fa5s.minus'))
        rotation_minus_btn.clicked.connect(self.decrease_rotation_angle)
        rotation_minus_btn.setFixedWidth(20)  # Small, compact button
        rotation_minus_btn.setFixedHeight(20)
        
        self.rotation_angle = QLineEdit(str(self.config["commands"]["default_values"]["rotation_angle"]))
        self.rotation_angle.setFixedWidth(60)
        
        rotation_plus_btn = QPushButton("+")
        rotation_plus_btn.setIcon(qta.icon('fa5s.plus'))
        rotation_plus_btn.clicked.connect(self.increase_rotation_angle)
        rotation_plus_btn.setFixedWidth(20)  # Small, compact button
        rotation_plus_btn.setFixedHeight(20)
        
        rotation_layout.addWidget(rotation_minus_btn)
        rotation_layout.addWidget(self.rotation_angle)
        rotation_layout.addWidget(rotation_plus_btn)
        device_layout.addLayout(rotation_layout, 3, 0, 1, 2)
        
        movement_layout = QHBoxLayout()
        movement_layout.addWidget(QLabel("Movement Step:"))
        
        movement_minus_btn = QPushButton("-")
        movement_minus_btn.setIcon(qta.icon('fa5s.minus'))
        movement_minus_btn.clicked.connect(self.decrease_movement_step)
        movement_minus_btn.setFixedWidth(20)  # Small, compact button
        movement_minus_btn.setFixedHeight(20)
        
        self.movement_step = QLineEdit(str(self.config["commands"]["default_values"]["movement_step"]))
        self.movement_step.setFixedWidth(60)
        
        movement_plus_btn = QPushButton("+")
        movement_plus_btn.setIcon(qta.icon('fa5s.plus'))
        movement_plus_btn.clicked.connect(self.increase_movement_step)
        movement_plus_btn.setFixedWidth(20)  # Small, compact button
        movement_plus_btn.setFixedHeight(20)
        
        movement_layout.addWidget(movement_minus_btn)
        movement_layout.addWidget(self.movement_step)
        movement_layout.addWidget(movement_plus_btn)
        device_layout.addLayout(movement_layout, 3, 2, 1, 2)

        # Add custom style for small buttons
        small_button_style = """
            QPushButton {
                padding: 0px;
                margin: 0px;
                border-radius: 2px;
            }
        """
        rotation_minus_btn.setStyleSheet(small_button_style)
        rotation_plus_btn.setStyleSheet(small_button_style)
        movement_minus_btn.setStyleSheet(small_button_style)
        movement_plus_btn.setStyleSheet(small_button_style)

        device_group.setLayout(device_layout)
        main_layout.addWidget(device_group)

        # UDP Configuration
        udp_group = QGroupBox("UDP Configuration")
        udp_layout = QGridLayout()
        
        # First row: IP and Port
        udp_layout.addWidget(QLabel("IP Address:"), 0, 0)
        self.udp_ip = QLineEdit(self.config["udp"]["ip"])
        udp_layout.addWidget(self.udp_ip, 0, 1)
        
        udp_layout.addWidget(QLabel("Port:"), 0, 2)
        self.udp_port = QLineEdit(str(self.config["udp"]["port"]))
        udp_layout.addWidget(self.udp_port, 0, 3)
        
        # Second row: Connect/Disconnect buttons
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setIcon(qta.icon('fa5s.plug'))
        self.connect_btn.clicked.connect(self.connect_device)
        udp_layout.addWidget(self.connect_btn, 1, 0, 1, 2)
        
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setIcon(qta.icon('fa5s.unlink'))
        self.disconnect_btn.clicked.connect(self.disconnect_device)
        udp_layout.addWidget(self.disconnect_btn, 1, 2, 1, 2)
        
        udp_group.setLayout(udp_layout)
        main_layout.addWidget(udp_group)
        
        # Device Control and Monitoring
        control_group = QGroupBox("Device Control and Monitoring")
        control_layout = QGridLayout()
        
        # Add control buttons with enhanced functionality
        self.buttons = {}
        button_configs = [
            ("X-Axis Control", "fa5s.arrows-alt-h", self.control_x_axis),
            ("Y-Axis Control", "fa5s.arrows-alt-v", self.control_y_axis),
            ("Z-Axis Control", "fa5s.arrows-alt", self.control_z_axis),
            ("Move Forward", "fa5s.arrow-up", self.move_forward),
            ("Reset Position", "fa5s.undo", self.reset_position),
            ("Calibrate", "fa5s.crosshairs", self.calibrate_device)
        ]
        
        for i, (text, icon, callback) in enumerate(button_configs):
            btn = QPushButton(text)
            btn.setIcon(qta.icon(icon))
            btn.setEnabled(False)
            btn.clicked.connect(callback)
            self.buttons[text] = btn
            control_layout.addWidget(btn, i // 2, i % 2)
            
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Set theme
        self.apply_theme()
        
        # Start monitoring timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_device_status)
        self.monitor_timer.start(1000)  # Update every second
        
    def update_device_list(self):
        """Update the device dropdown with available devices"""
        self.device_combo.clear()
        devices = self.lisu.get_available_devices()
        for device in devices:
            self.device_combo.addItem(device["name"])
            
    def update_udp_target(self):
        """Update UDP target when IP or port changes"""
        try:
            ip = self.udp_ip.currentText()
            port = int(self.udp_port.currentText())
            self.lisu.set_udp_target(ip, port)
        except ValueError:
            pass  # Ignore invalid port numbers
            
    def connect_device(self):
        """Connect to selected device"""
        device = self.device_type_combo.currentText()
        try:
            if device == "Gamepad_0":
                # Try to initialize the gamepad
                if pygame.joystick.get_count() > 0:
                    self.gamepad = pygame.joystick.Joystick(0)
                    self.gamepad.init()
                    self.status_bar.showMessage(f"Connected to {self.gamepad.get_name()}")
                    
                    # Reset previous axis values
                    self.prev_x_axis = 0.0
                    self.prev_y_axis = 0.0
                    
                    # Enable controls and start reading input
                    for btn in self.buttons.values():
                        btn.setEnabled(True)
                    
                    # Start reading gamepad input
                    self.is_reading_input = True
                    self.input_timer.start(16)  # ~60Hz update rate
                else:
                    self.status_bar.showMessage("No gamepad detected")
            else:
                # Handle other device types
                if self.lisu.connect_device(device):
                    self.status_bar.showMessage(f"Connected to {device}")
                    for btn in self.buttons.values():
                        btn.setEnabled(True)
                else:
                    self.status_bar.showMessage(f"Failed to connect to {device}")
        except Exception as e:
            self.status_bar.showMessage(f"Error connecting to {device}: {str(e)}")
            
    def configure_device(self):
        """Configure the current device"""
        device = self.device_type_combo.currentText()
        try:
            self.status_bar.showMessage(f"Configuring {device}...")
            # Add device-specific configuration here
        except Exception as e:
            self.status_bar.showMessage(f"Error configuring {device}: {str(e)}")
            
    def update_device_status(self):
        """Update device status information"""
        try:
            if self.gamepad and self.is_reading_input:
                self.status_bar.showMessage("Connected to Gamepad - Active")
            elif self.gamepad:
                self.status_bar.showMessage("Connected to Gamepad - Idle")
            else:
                self.status_bar.showMessage("Disconnected")
        except Exception as e:
            self.status_bar.showMessage(f"Error updating status: {str(e)}")
            
    def control_x_axis(self):
        """Control X-axis rotation"""
        try:
            angle = float(self.rotation_angle.text())
            cmd_type = self.cmd_combo.currentText()
            self.send_command(cmd_type, 1.0, 0.0, 0.0, angle)
        except ValueError:
            self.status_bar.showMessage("Invalid rotation angle value")
        except Exception as e:
            self.status_bar.showMessage(f"Error sending command: {str(e)}")
            
    def control_y_axis(self):
        """Control Y-axis rotation"""
        try:
            angle = float(self.rotation_angle.text())
            cmd_type = self.cmd_combo.currentText()
            self.send_command(cmd_type, 0.0, 1.0, 0.0, angle)
        except ValueError:
            self.status_bar.showMessage("Invalid rotation angle value")
        except Exception as e:
            self.status_bar.showMessage(f"Error sending command: {str(e)}")
            
    def control_z_axis(self):
        """Control Z-axis rotation"""
        try:
            angle = float(self.rotation_angle.text())
            cmd_type = self.cmd_combo.currentText()
            self.send_command(cmd_type, 0.0, 0.0, 1.0, angle)
        except ValueError:
            self.status_bar.showMessage("Invalid rotation angle value")
        except Exception as e:
            self.status_bar.showMessage(f"Error sending command: {str(e)}")
            
    def move_forward(self):
        """Move camera forward"""
        try:
            # Get user-specified movement step
            step = float(self.movement_step.text())
            self.send_command("move", 0.0, 0.0, step)  # Only 3 arguments for move
        except ValueError:
            self.status_bar.showMessage("Invalid movement step value")
        except Exception as e:
            self.status_bar.showMessage(f"Error sending command: {str(e)}")
            
    def reset_position(self):
        """Reset camera position"""
        try:
            # First translate to origin
            self.send_command("translate", 0.0, 0.0, 0.0)  # Only 3 arguments for translate
            
            # Then reset rotation (rotate to identity orientation)
            self.send_command("rotate", 0.0, 0.0, 1.0, 0.0)  # 4 arguments for rotate
            
            self.status_bar.showMessage("Position and orientation reset")
        except Exception as e:
            self.status_bar.showMessage(f"Error resetting position: {str(e)}")
            
    def calibrate_device(self):
        """Calibrate the device by resetting offsets and establishing neutral position."""
        try:
            device = self.device_type_combo.currentText()
            self.status_bar.showMessage(f"Starting calibration for {device}...")
            
            if device == "Gamepad_0" and self.gamepad:
                # Step 1: Stop current input reading
                was_reading = self.is_reading_input
                self.is_reading_input = False
                self.input_timer.stop()
                
                # Step 2: Process events to clear buffer
                pygame.event.pump()
                
                # Step 3: Read current axes to establish baseline
                x_baseline = self.gamepad.get_axis(0)
                y_baseline = self.gamepad.get_axis(1)
                
                # Step 4: Set calibration offsets
                self.x_offset = -x_baseline
                self.y_offset = -y_baseline
                
                # Step 5: Send reset command to visualisation
                try:
                    reset_cmd = "reset"  # The actual reset command for Drishti
                    self.udp_socket.sendto(
                        reset_cmd.encode(),
                        (self.udp_ip.text(), int(self.udp_port.text()))
                    )
                except Exception as e:
                    self.status_bar.showMessage(f"Warning: Could not send reset command: {str(e)}")
                
                # Step 6: Resume input reading if it was active
                if was_reading:
                    self.is_reading_input = True
                    self.input_timer.start(16)
                
                self.status_bar.showMessage(f"Calibration complete. Offsets: X={self.x_offset:.3f}, Y={self.y_offset:.3f}")
                
            elif device == "SpaceMouse":
                # SpaceMouse specific calibration
                try:
                    # Send specific reset commands for SpaceMouse
                    reset_cmd = "resetOrientation"
                    self.udp_socket.sendto(
                        reset_cmd.encode(),
                        (self.udp_ip.text(), int(self.udp_port.text()))
                    )
                    self.status_bar.showMessage("SpaceMouse orientation reset")
                except Exception as e:
                    self.status_bar.showMessage(f"Error resetting SpaceMouse: {str(e)}")
                    
            elif device == "Bluetooth_mouse":
                # Bluetooth mouse specific calibration
                try:
                    # Reset mouse position tracking
                    reset_cmd = "resetPosition"
                    self.udp_socket.sendto(
                        reset_cmd.encode(),
                        (self.udp_ip.text(), int(self.udp_port.text()))
                    )
                    self.status_bar.showMessage("Mouse position reset")
                except Exception as e:
                    self.status_bar.showMessage(f"Error resetting mouse position: {str(e)}")
            
        except Exception as e:
            self.status_bar.showMessage(f"Error during calibration: {str(e)}")
            
    def apply_theme(self):
        """Apply dark/light theme"""
        if darkdetect.isDark():
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    margin-top: 1em;
                    padding: 15px;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #3d3d3d;
                    border: none;
                    border-radius: 3px;
                    padding: 8px 15px;
                    color: white;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                }
                QPushButton:disabled {
                    background-color: #2d2d2d;
                    color: #666666;
                }
                QComboBox {
                    background-color: #3d3d3d;
                    border: 1px solid #4d4d4d;
                    border-radius: 3px;
                    padding: 5px;
                    color: white;
                    min-width: 150px;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    margin-top: 1em;
                    padding: 15px;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 8px 15px;
                    color: #000000;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QPushButton:disabled {
                    background-color: #f0f0f0;
                    color: #999999;
                }
                QComboBox {
                    background-color: white;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 5px;
                    color: #000000;
                    min-width: 150px;
                }
                QLabel {
                    color: #000000;
                }
            """) 

    def create_logo(self, label):
        """Create the LISU logo"""
        # Create a pixmap with transparent background
        pixmap = QPixmap(200, 200)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Create painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw outer circle
        pen = QPen(QColor("#000000"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(10, 10, 180, 180)
        
        # Draw VR goggles
        pen.setColor(QColor("#FF6B2B"))  # Orange color
        pen.setWidth(3)
        painter.setPen(pen)
        
        # Create goggles path
        goggles = QPainterPath()
        goggles.moveTo(50, 70)
        goggles.lineTo(150, 70)
        goggles.lineTo(150, 100)
        goggles.lineTo(120, 100)
        goggles.lineTo(120, 85)
        goggles.lineTo(80, 85)
        goggles.lineTo(80, 100)
        goggles.lineTo(50, 100)
        goggles.lineTo(50, 70)
        
        # Draw goggles
        painter.drawPath(goggles)
        
        # Draw LISU text
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor("#000000")))  # Set text color to black
        painter.drawText(pixmap.rect().adjusted(0, 100, 0, 0), Qt.AlignmentFlag.AlignCenter, "LISU")
        
        painter.end()
        
        # Set the pixmap to the label
        label.setPixmap(pixmap)
        label.setScaledContents(True) 

    def on_visualisation_changed(self, vis_name):
        """Handle visualisation target change."""
        if vis_name in self.config["visualisations"]["target_configs"]:
            vis_config = self.config["visualisations"]["target_configs"][vis_name]
            self.udp_ip.setText(vis_config["udp_ip"])
            self.udp_port.setText(str(vis_config["udp_port"]))
            self.status_bar.showMessage(f"Selected visualisation: {vis_name} ({vis_config['description']})")

    def on_command_changed(self, cmd_name):
        """Handle command type change."""
        if cmd_name in self.config["commands"]["command_formats"]:
            cmd_format = self.config["commands"]["command_formats"][cmd_name]
            self.status_bar.showMessage(f"Selected command type: {cmd_name} (Format: {cmd_format})")

    def send_command(self, cmd_type, x, y, z, scale=None):
        """Centralized command sending function"""
        try:
            if cmd_type in self.config["commands"]["command_formats"]:
                command_format = self.config["commands"]["command_formats"][cmd_type]
                print(f"Debug - Command format: {command_format}")
                
                # Count format specifiers to determine parameter count
                param_count = command_format.count('%.2f')
                
                # Prepare arguments based on parameter count
                if param_count == 3:
                    args = (x, y, z)
                    print(f"Debug - Arguments (3): x={x}, y={y}, z={z}")
                elif param_count == 4:
                    args = (x, y, z, scale)
                    print(f"Debug - Arguments (4): x={x}, y={y}, z={z}, scale={scale}")
                else:
                    print(f"Debug - Unsupported parameter count: {param_count}")
                    return False
                
                # Format command with appropriate number of arguments
                command = command_format % args
                
                # Send via UDP
                ip = self.udp_ip.text()
                port = int(self.udp_port.text())
                
                self.udp_socket.sendto(command.encode(), (ip, port))
                #print(f"UDP sent -> {command} to {ip}:{port}")
                
                # Update status message
                if param_count == 3:
                    self.status_bar.showMessage(f"Sent {cmd_type}: ({x:.2f}, {y:.2f}, {z:.2f})")
                else:
                    self.status_bar.showMessage(f"Sent {cmd_type}: ({x:.2f}, {y:.2f}, {z:.2f}), scale={scale}")
                return True
            else:
                error_msg = f"Unknown command type: {cmd_type}"
                print(f"UDP error: {error_msg}")
                self.status_bar.showMessage(error_msg)
                return False
        except Exception as e:
            print(f"UDP error: {str(e)}")
            print(f"Debug - Failed command type: {cmd_type}")
            print(f"Debug - Command format: {command_format}")
            print(f"Debug - Arguments: x={x}, y={y}, z={z}, scale={scale}")
            self.status_bar.showMessage(f"Error sending command: {str(e)}")
            return False

    def log_message(self, message):
        """Show message in status bar."""
        self.status_bar.showMessage(message, 3000)  # Show for 3 seconds
        
    def disconnect_device(self):
        """Disconnect from the current device."""
        device = self.device_type_combo.currentText()
        try:
            if device == "Gamepad_0" and self.gamepad:
                # Stop reading input and uninitialize gamepad
                self.is_reading_input = False
                self.input_timer.stop()
                self.gamepad.quit()
                self.gamepad = None
                
                self.status_bar.showMessage("Gamepad disconnected")
                for btn in self.buttons.values():
                    btn.setEnabled(False)
            else:
                # Handle other device types
                self.status_bar.showMessage(f"Disconnecting from device: {device}")
                for btn in self.buttons.values():
                    btn.setEnabled(False)
        except Exception as e:
            self.status_bar.showMessage(f"Error disconnecting from device: {str(e)}")
            
    def read_gamepad_input(self):
        """Read and process gamepad input with calibration offsets."""
        if not self.is_reading_input or not self.gamepad:
            return
            
        try:
            # Process pygame events
            pygame.event.pump()
            
            # Read axis values and apply calibration offsets
            x_axis = self.gamepad.get_axis(0) + getattr(self, 'x_offset', 0.0)
            y_axis = self.gamepad.get_axis(1) + getattr(self, 'y_offset', 0.0)
            
            # Store previous axis values if not set
            if not hasattr(self, 'prev_x_axis'):
                self.prev_x_axis = x_axis
            if not hasattr(self, 'prev_y_axis'):
                self.prev_y_axis = y_axis
            
            # Only send commands if there's significant movement (avoid drift)
            threshold = 0.1
            current_time = datetime.now()
            
            # Add rate limiting - only send every 100ms (10Hz) when movement is detected
            if not hasattr(self, 'last_send_time'):
                self.last_send_time = current_time
                
            time_diff = (current_time - self.last_send_time).total_seconds()
            
            # Check if there's actual movement (change in axis values)
            x_movement = abs(x_axis - self.prev_x_axis) > 0.01
            y_movement = abs(y_axis - self.prev_y_axis) > 0.01
            
            # Only send if there's significant position AND movement
            if (abs(x_axis) > threshold or abs(y_axis) > threshold) and (x_movement or y_movement):
                if time_diff >= 0.1:  # 100ms rate limiting
                    try:
                        # Get user-specified rotation angle and command type
                        scale = float(self.rotation_angle.text())
                        cmd_type = self.cmd_combo.currentText()
                        
                        # Send command through centralized function
                        self.send_command(cmd_type, x_axis, -y_axis, 0.0, scale)
                        
                        # Update last send time
                        self.last_send_time = current_time
                            
                    except ValueError:
                        print("UDP error: Invalid rotation angle value")
                        self.status_bar.showMessage("Invalid rotation angle value")
            
            # Store current values for next comparison
            self.prev_x_axis = x_axis
            self.prev_y_axis = y_axis
                    
        except Exception as e:
            print(f"UDP error: {str(e)}")
            self.status_bar.showMessage(f"Error reading gamepad: {str(e)}")
            self.is_reading_input = False
            self.input_timer.stop()

    def closeEvent(self, event):
        """Clean up resources when closing the window."""
        try:
            # Stop input reading
            self.is_reading_input = False
            self.input_timer.stop()
            
            # Clean up pygame
            if self.gamepad:
                self.gamepad.quit()
            pygame.quit()
            
            # Close UDP socket
            self.udp_socket.close()
        except:
            pass
        super().closeEvent(event) 

    def increase_rotation_angle(self):
        """Increase rotation angle by 1 degree"""
        try:
            current = float(self.rotation_angle.text())
            self.rotation_angle.setText(str(current + 1))
        except ValueError:
            self.rotation_angle.setText("1")

    def decrease_rotation_angle(self):
        """Decrease rotation angle by 1 degree"""
        try:
            current = float(self.rotation_angle.text())
            if current > 1:  # Prevent negative or zero angles
                self.rotation_angle.setText(str(current - 1))
        except ValueError:
            self.rotation_angle.setText("1")

    def increase_movement_step(self):
        """Increase movement step by 1"""
        try:
            current = float(self.movement_step.text())
            self.movement_step.setText(str(current + 1))
        except ValueError:
            self.movement_step.setText("1")

    def decrease_movement_step(self):
        """Decrease movement step by 1"""
        try:
            current = float(self.movement_step.text())
            if current > 1:  # Prevent negative or zero steps
                self.movement_step.setText(str(current - 1))
        except ValueError:
            self.movement_step.setText("1") 