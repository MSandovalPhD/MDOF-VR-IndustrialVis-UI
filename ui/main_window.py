from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QStatusBar,
                             QGroupBox, QGridLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPen, QColor, QPainterPath
import qtawesome as qta
import darkdetect
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self, lisu_manager):
        super().__init__()
        self.lisu = lisu_manager
        self.setup_ui()
        
    def setup_ui(self):
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
        
        # Logo
        logo_label = QLabel()
        logo_label.setFixedSize(75, 75)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Load logo from resources
        logo_svg = Path("resources/logo.svg")
        logo_png = Path("resources/logo.png")
        
        if logo_png.exists():
            pixmap = QPixmap(str(logo_png))
        elif logo_svg.exists():
            try:
                pixmap = QPixmap(str(logo_svg))
            except:
                self.status_bar.showMessage("Error loading SVG logo")
                return
        else:
            self.status_bar.showMessage("Logo file not found")
            return
            
        scaled_pixmap = pixmap.scaled(
            75, 75,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        logo_label.setPixmap(scaled_pixmap)
        
        # Welcome message
        welcome_text = QLabel(
            "Welcome to the Layered Interaction System for User-Modes (LISU)\n"
            "Control VR visualisations, manipulate 3D models and navigate virtual environments"
        )
        welcome_text.setWordWrap(True)
        welcome_font = QFont()
        welcome_font.setPointSize(10)        
        welcome_text.setFont(welcome_font)
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        
        # Add widgets to header with spacing
        header_layout.addWidget(logo_label)
        header_layout.addSpacing(20)  # Increased space between logo and text
        header_layout.addWidget(welcome_text)  # 1 is stretch factor
        
        # Add header to main layout
        main_layout.addWidget(header_container, 0, Qt.AlignmentFlag.AlignLeft)
        
        # Add small spacing after header
        main_layout.addSpacing(10)
        
        # Create device selection group
        device_group = QGroupBox("Device Selection and Configuration")
        device_layout = QGridLayout()
        
        # Device dropdown with available devices
        self.device_combo = QComboBox()
        self.update_device_list()
        device_layout.addWidget(QLabel("Select Device:"), 0, 0)
        device_layout.addWidget(self.device_combo, 0, 1)
        
        # Add UDP Configuration
        self.udp_ip = QComboBox()
        self.udp_ip.addItems(["127.0.0.1", "192.168.1.1", "Custom..."])
        self.udp_ip.setEditable(True)
        self.udp_ip.currentTextChanged.connect(self.update_udp_target)
        device_layout.addWidget(QLabel("UDP IP:"), 1, 0)
        device_layout.addWidget(self.udp_ip, 1, 1)
        
        self.udp_port = QComboBox()
        self.udp_port.addItems(["7755", "8080", "9000", "Custom..."])
        self.udp_port.setEditable(True)
        self.udp_port.currentTextChanged.connect(self.update_udp_target)
        device_layout.addWidget(QLabel("UDP Port:"), 2, 0)
        device_layout.addWidget(self.udp_port, 2, 1)
        
        # Connect and Configure buttons
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect Device")
        self.connect_btn.setIcon(qta.icon('fa5s.plug'))
        self.connect_btn.clicked.connect(self.connect_device)
        
        self.configure_btn = QPushButton("Configure")
        self.configure_btn.setIcon(qta.icon('fa5s.cog'))
        self.configure_btn.clicked.connect(self.configure_device)
        
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.configure_btn)
        device_layout.addLayout(button_layout, 3, 0, 1, 2)
        
        device_group.setLayout(device_layout)
        main_layout.addWidget(device_group)
        
        # Create control group
        control_group = QGroupBox("Device Control and Monitoring")
        control_layout = QGridLayout()
        
        # Add control buttons with enhanced functionality
        self.buttons = {}
        button_configs = [
            ("X-Axis Control", "fa5s.arrows-alt-h", self.control_x_axis),
            ("Y-Axis Control", "fa5s.arrows-alt-v", self.control_y_axis),
            ("Z-Axis Control", "fa5s.arrows-alt", self.control_z_axis),
            ("Rotation Control", "fa5s.sync", self.control_rotation),
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
        
        # Add monitoring section
        monitor_group = QGroupBox("Device Status Monitor")
        monitor_layout = QGridLayout()
        
        # Add monitoring labels
        self.status_labels = {}
        monitor_items = ["Connection Status", "Input Rate", "Signal Strength", "Battery Level"]
        
        for i, item in enumerate(monitor_items):
            label = QLabel(f"{item}:")
            value = QLabel("N/A")
            value.setStyleSheet("color: gray;")
            self.status_labels[item] = value
            monitor_layout.addWidget(label, i, 0)
            monitor_layout.addWidget(value, i, 1)
        
        monitor_group.setLayout(monitor_layout)
        main_layout.addWidget(monitor_group)
        
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
        device = self.device_combo.currentText()
        try:
            if self.lisu.connect_device(device):
                self.status_bar.showMessage(f"Connected to {device}")
                for btn in self.buttons.values():
                    btn.setEnabled(True)
                self.status_labels["Connection Status"].setText("Connected")
                self.status_labels["Connection Status"].setStyleSheet("color: green;")
            else:
                self.status_bar.showMessage(f"Failed to connect to {device}")
                self.status_labels["Connection Status"].setText("Connection Failed")
                self.status_labels["Connection Status"].setStyleSheet("color: red;")
        except Exception as e:
            self.status_bar.showMessage(f"Error connecting to {device}: {str(e)}")
            
    def configure_device(self):
        """Configure the current device"""
        device = self.device_combo.currentText()
        try:
            self.status_bar.showMessage(f"Configuring {device}...")
            # Add device-specific configuration here
        except Exception as e:
            self.status_bar.showMessage(f"Error configuring {device}: {str(e)}")
            
    def update_device_status(self):
        """Update device status information"""
        status = self.lisu.get_device_status()
        
        # Update status labels
        self.status_labels["Connection Status"].setText(
            "Connected" if status["connected"] else "Disconnected"
        )
        self.status_labels["Connection Status"].setStyleSheet(
            "color: green;" if status["connected"] else "color: red;"
        )
        self.status_labels["Input Rate"].setText(f"{status.get('input_rate', 0)} Hz")
        self.status_labels["Signal Strength"].setText(status.get('signal_strength', 'Unknown'))
        self.status_labels["Battery Level"].setText(status.get('battery_level', 'Unknown'))
        
    def control_x_axis(self):
        """Control X-axis"""
        try:
            if self.lisu.send_command("rotation", {"x": 1.0, "y": 0.0, "z": 0.0}):
                self.status_bar.showMessage("X-axis control activated")
            else:
                self.status_bar.showMessage("Failed to activate X-axis control")
        except Exception as e:
            self.status_bar.showMessage(f"Error controlling X-axis: {str(e)}")
            
    def control_y_axis(self):
        """Control Y-axis"""
        try:
            if self.lisu.send_command("rotation", {"x": 0.0, "y": 1.0, "z": 0.0}):
                self.status_bar.showMessage("Y-axis control activated")
            else:
                self.status_bar.showMessage("Failed to activate Y-axis control")
        except Exception as e:
            self.status_bar.showMessage(f"Error controlling Y-axis: {str(e)}")
            
    def control_z_axis(self):
        """Control Z-axis"""
        try:
            if self.lisu.send_command("rotation", {"x": 0.0, "y": 0.0, "z": 1.0}):
                self.status_bar.showMessage("Z-axis control activated")
            else:
                self.status_bar.showMessage("Failed to activate Z-axis control")
        except Exception as e:
            self.status_bar.showMessage(f"Error controlling Z-axis: {str(e)}")
            
    def control_rotation(self):
        """Control rotation"""
        try:
            if self.lisu.send_command("rotation", {"x": 0.5, "y": 0.5, "z": 0.5}):
                self.status_bar.showMessage("Rotation control activated")
            else:
                self.status_bar.showMessage("Failed to activate rotation control")
        except Exception as e:
            self.status_bar.showMessage(f"Error controlling rotation: {str(e)}")
            
    def reset_position(self):
        """Reset device position"""
        try:
            if self.lisu.send_command("rotation", {"x": 0.0, "y": 0.0, "z": 0.0}):
                self.status_bar.showMessage("Position reset")
            else:
                self.status_bar.showMessage("Failed to reset position")
        except Exception as e:
            self.status_bar.showMessage(f"Error resetting position: {str(e)}")
            
    def calibrate_device(self):
        """Calibrate the device"""
        try:
            self.status_bar.showMessage("Calibrating device...")
            # Add device-specific calibration here
        except Exception as e:
            self.status_bar.showMessage(f"Error calibrating device: {str(e)}")
            
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