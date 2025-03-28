from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QStatusBar,
                             QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
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
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create device selection group
        device_group = QGroupBox("Device Selection")
        device_layout = QGridLayout()
        
        # Device dropdown
        self.device_combo = QComboBox()
        self.device_combo.addItems(["Bluetooth Mouse", "SpaceMouse", "Gamepad"])
        device_layout.addWidget(QLabel("Select Device:"), 0, 0)
        device_layout.addWidget(self.device_combo, 0, 1)
        
        # Connect button
        self.connect_btn = QPushButton("Connect Device")
        self.connect_btn.setIcon(qta.icon('fa5s.plug'))
        self.connect_btn.clicked.connect(self.connect_device)
        device_layout.addWidget(self.connect_btn, 0, 2)
        
        device_group.setLayout(device_layout)
        main_layout.addWidget(device_group)
        
        # Create control group
        control_group = QGroupBox("Device Control")
        control_layout = QGridLayout()
        
        # Add control buttons
        self.buttons = {}
        button_configs = [
            ("X-Axis", "fa5s.arrows-alt-h"),
            ("Y-Axis", "fa5s.arrows-alt-v"),
            ("Z-Axis", "fa5s.arrows-alt"),
            ("Rotate", "fa5s.sync"),
            ("Reset", "fa5s.undo")
        ]
        
        for i, (text, icon) in enumerate(button_configs):
            btn = QPushButton(text)
            btn.setIcon(qta.icon(icon))
            btn.setEnabled(False)
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
                    padding-top: 10px;
                }
                QPushButton {
                    background-color: #3d3d3d;
                    border: none;
                    border-radius: 3px;
                    padding: 5px 10px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                }
                QPushButton:disabled {
                    background-color: #2d2d2d;
                }
                QComboBox {
                    background-color: #3d3d3d;
                    border: 1px solid #4d4d4d;
                    border-radius: 3px;
                    padding: 5px;
                    color: white;
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
                    padding-top: 10px;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 5px 10px;
                    color: #000000;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QPushButton:disabled {
                    background-color: #f0f0f0;
                }
                QComboBox {
                    background-color: white;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 5px;
                    color: #000000;
                }
            """)
            
    def connect_device(self):
        device = self.device_combo.currentText()
        try:
            # Here we would call the LISU framework to connect to the device
            self.status_bar.showMessage(f"Connected to {device}")
            for btn in self.buttons.values():
                btn.setEnabled(True)
        except Exception as e:
            self.status_bar.showMessage(f"Error connecting to {device}: {str(e)}") 