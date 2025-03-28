from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QStatusBar,
                             QGroupBox, QGridLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import qtawesome as qta
import darkdetect

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
        
        # Add title
        title_label = QLabel("LISU Framework")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Create device selection group
        device_group = QGroupBox("Device Selection and Configuration")
        device_layout = QGridLayout()
        
        # Device dropdown with enhanced options
        self.device_combo = QComboBox()
        self.device_combo.addItems([
            "Bluetooth Mouse",
            "SpaceMouse",
            "Gamepad",
            "3DConnexion SpaceMouse",
            "Logitech Gaming Mouse",
            "Xbox Controller"
        ])
        device_layout.addWidget(QLabel("Select Device:"), 0, 0)
        device_layout.addWidget(self.device_combo, 0, 1)
        
        # Add UDP Configuration
        self.udp_ip = QComboBox()
        self.udp_ip.addItems(["127.0.0.1", "192.168.1.1", "Custom..."])
        self.udp_ip.setEditable(True)
        device_layout.addWidget(QLabel("UDP IP:"), 1, 0)
        device_layout.addWidget(self.udp_ip, 1, 1)
        
        self.udp_port = QComboBox()
        self.udp_port.addItems(["7755", "8080", "9000", "Custom..."])
        self.udp_port.setEditable(True)
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
        
    def apply_theme(self):
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
            
    def connect_device(self):
        device = self.device_combo.currentText()
        try:
            # Call LISU framework to connect to the device
            self.lisu.connect_device(device)
            self.status_bar.showMessage(f"Connected to {device}")
            for btn in self.buttons.values():
                btn.setEnabled(True)
            self.status_labels["Connection Status"].setText("Connected")
            self.status_labels["Connection Status"].setStyleSheet("color: green;")
        except Exception as e:
            self.status_bar.showMessage(f"Error connecting to {device}: {str(e)}")
            
    def configure_device(self):
        device = self.device_combo.currentText()
        try:
            # Call LISU framework to configure the device
            self.status_bar.showMessage(f"Configuring {device}...")
        except Exception as e:
            self.status_bar.showMessage(f"Error configuring {device}: {str(e)}")
            
    def update_device_status(self):
        if self.lisu.current_device:
            # Update monitoring information
            self.status_labels["Input Rate"].setText("60 Hz")
            self.status_labels["Signal Strength"].setText("Excellent")
            self.status_labels["Battery Level"].setText("100%")
            
    def control_x_axis(self):
        self.status_bar.showMessage("Controlling X-Axis...")
        
    def control_y_axis(self):
        self.status_bar.showMessage("Controlling Y-Axis...")
        
    def control_z_axis(self):
        self.status_bar.showMessage("Controlling Z-Axis...")
        
    def control_rotation(self):
        self.status_bar.showMessage("Controlling Rotation...")
        
    def reset_position(self):
        self.status_bar.showMessage("Resetting Position...")
        
    def calibrate_device(self):
        self.status_bar.showMessage("Calibrating Device...") 