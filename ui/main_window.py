"""
© Mario Sandoval Olive 2024. All rights reserved.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QStatusBar,
                             QGroupBox, QGridLayout, QSpacerItem, QSizePolicy,
                             QLineEdit, QTextEdit, QTabWidget, QFrame)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPen, QColor, QPainterPath
import qtawesome as qta
import darkdetect
from pathlib import Path
import socket
import json
from datetime import datetime
import pygame
import os
from .mapping_window import MappingWindow

class MainWindow(QMainWindow):
    def __init__(self, lisu_manager):
        super().__init__()
        self.lisu_manager = lisu_manager
        self.config = self.load_config()
        self.selected_device = None
        self.udp_socket = None
        self.last_command_time = 0
        self.command_interval = 0.05  # 50ms between commands
        
        # Initialize mapping control attributes
        self.axis_mapping_controls = []
        self.button_mapping_controls = []
        self.axis_mapping_layout = QGridLayout()
        self.button_mapping_layout = QGridLayout()
        
        # Initialize device capabilities
        self.device_capabilities = {
            "Gamepad_0": {"axes": 4, "buttons": 8},
            "Bluetooth_mouse": {"axes": 2, "buttons": 3},
            "SpaceMouse": {"axes": 6, "buttons": 2}
        }
        
        # Initialize status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setFont(QFont("Roboto", 10)) 
        self.status_bar.showMessage("Ready")
        
        # Initialize mapping buttons
        self.save_mapping_button = QPushButton("Save Mapping")
        self.save_mapping_button.setIcon(qta.icon('fa5s.save', color='white'))
        self.save_mapping_button.setFont(QFont("Roboto", 10))
        
        self.load_mapping_button = QPushButton("Load Mapping")
        self.load_mapping_button.setIcon(qta.icon('fa5s.folder-open', color='white'))
        self.load_mapping_button.setFont(QFont("Roboto", 10))
        
        self.setup_ui()
        self.setup_gamepad()
        
    def setup_ui(self):
        """Set up the main window UI"""
        self.setWindowTitle("LISU Control Interface")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
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
        welcome_font = QFont("Roboto", 11)
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
        
        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.setFont(QFont("Roboto", 12))
        
        # Create tabs
        device_tab = QWidget()
        control_tab = QWidget()
        mapping_tab = QWidget()
        settings_tab = QWidget()
        
        # Set up tab layouts
        device_layout = QVBoxLayout(device_tab)
        control_layout = QVBoxLayout(control_tab)
        mapping_layout = QVBoxLayout(mapping_tab)
        settings_layout = QVBoxLayout(settings_tab)
        
        # Add tabs to widget with icons and tooltips
        device_tab_index = tab_widget.addTab(device_tab, qta.icon('fa5s.gamepad', color='white'), "Device")
        tab_widget.setTabToolTip(device_tab_index, 
            "Configure your input device, select visualization target, and set up UDP connection")
        
        control_tab_index = tab_widget.addTab(control_tab, qta.icon('fa5s.sliders-h', color='white'), "Control")
        tab_widget.setTabToolTip(control_tab_index, 
            "Control device movement and rotation with buttons and input device")
        
        mapping_tab_index = tab_widget.addTab(mapping_tab, qta.icon('fa5s.cog', color='white'), "Mapping")
        tab_widget.setTabToolTip(mapping_tab_index, 
            "Customize how your input device's axes and buttons map to different functions")
        
        settings_tab_index = tab_widget.addTab(settings_tab, qta.icon('fa5s.cogs', color='white'), "Settings")
        tab_widget.setTabToolTip(settings_tab_index, 
            "Configure application settings, theme, and other preferences")
        
        # Add tab widget to main layout
        main_layout.addWidget(tab_widget)
        
        # Set up Device tab content (Device Selection and UDP Configuration)
        self.setup_device_tab(device_layout)
        
        # Set up Control tab content (Device Control)
        self.setup_control_tab(control_layout)
        
        # Set up Mapping tab content
        self.setup_mapping_tab(mapping_layout)
        
        # Set up Settings tab content
        self.setup_settings_tab(settings_layout)
        
        # Apply styling
        self.apply_styling()
        
    def setup_device_tab(self, layout):
        """Set up the Device tab content"""
        # Device Selection and Configuration
        device_group = QGroupBox("Device Selection and Configuration")
        device_group.setFont(QFont("Roboto", 14, QFont.Weight.Bold))
        device_layout = QGridLayout()
        device_layout.setContentsMargins(20, 20, 20, 20)
        device_layout.setSpacing(15)
        
        # First row: Device Selection and Visualisation Target
        device_layout.addWidget(QLabel("Select Device:"), 0, 0)
        self.device_type_combo = QComboBox()
        self.device_type_combo.setFont(QFont("Roboto", 10))
        self.device_type_combo.addItems(["Gamepad_0", "Bluetooth_mouse", "SpaceMouse"])
        device_layout.addWidget(self.device_type_combo, 0, 1)
        
        # Add Configure Mapping button
        self.configure_mapping_btn = QPushButton("Configure Mapping")
        self.configure_mapping_btn.setIcon(qta.icon('fa5s.cog', color='white'))
        self.configure_mapping_btn.setFont(QFont("Roboto", 10))
        self.configure_mapping_btn.clicked.connect(self.open_mapping_window)
        device_layout.addWidget(self.configure_mapping_btn, 0, 2)
        
        device_layout.addWidget(QLabel("Visualisation Target:"), 0, 3)
        self.vis_combo = QComboBox()
        self.vis_combo.setFont(QFont("Roboto", 12))
        self.vis_combo.addItems(self.config.get("visualisations", {}).get("available_targets", []))
        self.vis_combo.currentTextChanged.connect(self.on_visualisation_changed)
        device_layout.addWidget(self.vis_combo, 0, 4)
        
        # Second row: Command Type
        device_layout.addWidget(QLabel("Command Type:"), 1, 0)
        self.cmd_combo = QComboBox()
        self.cmd_combo.setFont(QFont("Roboto", 10))
        self.cmd_combo.addItems(self.config.get("commands", {}).get("available_commands", []))
        self.cmd_combo.currentTextChanged.connect(self.on_command_changed)
        device_layout.addWidget(self.cmd_combo, 1, 1, 1, 4)
        
        # Third row: Movement Parameters
        device_layout.addWidget(QLabel("Rotation Angle:"), 2, 0)
        rotation_layout = QHBoxLayout()
        rotation_layout.setSpacing(5)  # Reduce spacing between elements
        self.rotation_input = QLineEdit("40.0")
        self.rotation_input.setFont(QFont("Roboto", 12))
        self.rotation_input.setFixedWidth(80)  # Reduce width
        rotation_layout.addWidget(self.rotation_input)
        
        # Add +/- buttons for rotation
        self.rotation_plus_btn = QPushButton("+")
        self.rotation_plus_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        self.rotation_plus_btn.setFixedWidth(30)  # Reduce width
        self.rotation_plus_btn.clicked.connect(lambda: self.adjust_rotation(1))
        rotation_layout.addWidget(self.rotation_plus_btn)
        
        self.rotation_minus_btn = QPushButton("-")
        self.rotation_minus_btn.setIcon(qta.icon('fa5s.minus', color='white'))
        self.rotation_minus_btn.setFixedWidth(30)  # Reduce width
        self.rotation_minus_btn.clicked.connect(lambda: self.adjust_rotation(-1))
        rotation_layout.addWidget(self.rotation_minus_btn)
        
        device_layout.addLayout(rotation_layout, 2, 1, 1, 2)
        
        device_layout.addWidget(QLabel("Movement Step:"), 2, 3)
        step_layout = QHBoxLayout()
        step_layout.setSpacing(5)  # Reduce spacing between elements
        self.step_input = QLineEdit("1.0")
        self.step_input.setFont(QFont("Roboto", 10))
        self.step_input.setFixedWidth(80)  # Reduce width
        step_layout.addWidget(self.step_input)
        
        # Add +/- buttons for step
        self.step_plus_btn = QPushButton("+")
        self.step_plus_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        self.step_plus_btn.setFixedWidth(30)  # Reduce width
        self.step_plus_btn.clicked.connect(lambda: self.adjust_step(1))
        step_layout.addWidget(self.step_plus_btn)
        
        self.step_minus_btn = QPushButton("-")
        self.step_minus_btn.setIcon(qta.icon('fa5s.minus', color='white'))
        self.step_minus_btn.setFixedWidth(30)  # Reduce width
        self.step_minus_btn.clicked.connect(lambda: self.adjust_step(-1))
        step_layout.addWidget(self.step_minus_btn)
        
        device_layout.addLayout(step_layout, 2, 4)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        
        # UDP Configuration
        udp_group = QGroupBox("UDP Configuration")
        udp_group.setFont(QFont("Roboto", 12, QFont.Weight.Bold))
        udp_layout = QGridLayout()
        udp_layout.setContentsMargins(20, 20, 20, 20)
        udp_layout.setSpacing(15)
        
        udp_layout.addWidget(QLabel("IP Address:"), 0, 0)
        self.udp_ip = QLineEdit(self.config["udp"]["ip"])
        self.udp_ip.setFont(QFont("Roboto", 10))
        udp_layout.addWidget(self.udp_ip, 0, 1)
        
        udp_layout.addWidget(QLabel("Port:"), 0, 2)
        self.udp_port = QLineEdit(str(self.config["udp"]["port"]))
        self.udp_port.setFont(QFont("Roboto", 10))
        udp_layout.addWidget(self.udp_port, 0, 3)
        
        # Create connect and disconnect buttons
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setIcon(qta.icon('fa5s.plug', color='white'))
        self.connect_btn.setFont(QFont("Roboto", 10))
        self.connect_btn.clicked.connect(self.connect_device)
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setIcon(qta.icon('fa5s.unlink', color='white'))
        self.disconnect_btn.setFont(QFont("Roboto", 10))
        self.disconnect_btn.clicked.connect(self.disconnect_device)
        
        udp_layout.addWidget(self.connect_btn, 0, 4)
        udp_layout.addWidget(self.disconnect_btn, 0, 5)
        
        udp_group.setLayout(udp_layout)
        layout.addWidget(udp_group)
        
        # Add stretch to push everything up
        layout.addStretch()
        
    def setup_control_tab(self, layout):
        """Set up the Control tab content"""
        # Device Control
        control_group = QGroupBox("Device Control")
        control_group.setFont(QFont("Roboto", 12, QFont.Weight.Bold))
        control_layout = QGridLayout()
        control_layout.setContentsMargins(20, 20, 20, 20)
        control_layout.setSpacing(15)
        
        # Translation Controls
        translation_controls = [
            ("X-Axis Control", "fa5s.arrows-alt-h", self.control_x_axis),
            ("Y-Axis Control", "fa5s.arrows-alt-v", self.control_y_axis),
            ("Z-Axis Control", "fa5s.arrows-alt", self.control_z_axis)
        ]
        
        # Rotation Controls
        rotation_controls = [
            ("Yaw Control", "fa5s.undo", self.control_yaw),
            ("Pitch Control", "fa5s.undo-alt", self.control_pitch),
            ("Roll Control", "fa5s.sync", self.control_roll)
        ]
        
        # Utility Controls
        utility_controls = [
            ("Move Forward", "fa5s.arrow-up", self.move_forward),
            ("Reset Position", "fa5s.undo", self.reset_position),
            ("Calibrate", "fa5s.cog", self.calibrate_device)
        ]
        
        # Add all controls to layout
        row = 0
        for controls in [translation_controls, rotation_controls, utility_controls]:
            for i, (text, icon, callback) in enumerate(controls):
                btn = QPushButton(text)
                btn.setIcon(qta.icon(icon, color='white'))
                btn.setFont(QFont("Roboto", 10))
                btn.clicked.connect(callback)
                control_layout.addWidget(btn, row, i)
            row += 1
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Add stretch to push everything up
        layout.addStretch()
        
    def setup_mapping_tab(self, layout):
        """Set up the Mapping tab content"""
        # Create tab widget for mapping
        mapping_tab_widget = QTabWidget()
        mapping_tab_widget.setFont(QFont("Roboto", 12))
        
        # Create tabs for axis and button mapping
        axis_tab = QWidget()
        button_tab = QWidget()
        
        # Set up tab layouts
        axis_layout = QVBoxLayout(axis_tab)
        button_layout = QVBoxLayout(button_tab)
        
        # Add tabs to widget
        mapping_tab_widget.addTab(axis_tab, "Axis Mapping")
        mapping_tab_widget.addTab(button_tab, "Button Mapping")
        
        # Set up Axis Mapping tab
        axis_group = QGroupBox("Axis Mapping Configuration")
        axis_group.setFont(QFont("Roboto", 12, QFont.Weight.Bold))
        axis_content_layout = QVBoxLayout()
        axis_content_layout.setContentsMargins(20, 20, 20, 20)
        axis_content_layout.setSpacing(15)
        
        # Add axis mapping description
        axis_label = QLabel(
            "Configure how your input device's axes map to different control functions.\n"
            "This allows you to customize the behavior of your device for optimal control."
        )
        axis_label.setFont(QFont("Roboto", 10))
        axis_label.setWordWrap(True)
        axis_content_layout.addWidget(axis_label)
        
        # Add headers for axis mapping
        self.axis_mapping_layout.addWidget(QLabel("Axis"), 0, 0)
        self.axis_mapping_layout.addWidget(QLabel("Function"), 0, 1)
        axis_content_layout.addLayout(self.axis_mapping_layout)
        
        # Add save/load buttons for axis mapping
        axis_button_layout = QHBoxLayout()
        axis_save_btn = QPushButton("Save Axis Mapping")
        axis_save_btn.setIcon(qta.icon('fa5s.save', color='white'))
        axis_save_btn.setFont(QFont("Roboto", 10))
        axis_save_btn.clicked.connect(lambda: self.save_mapping("axis"))
        
        axis_load_btn = QPushButton("Load Axis Mapping")
        axis_load_btn.setIcon(qta.icon('fa5s.folder-open', color='white'))
        axis_load_btn.setFont(QFont("Roboto", 10))
        axis_load_btn.clicked.connect(lambda: self.load_mapping("axis"))
        
        axis_button_layout.addWidget(axis_save_btn)
        axis_button_layout.addWidget(axis_load_btn)
        axis_content_layout.addLayout(axis_button_layout)
        
        axis_group.setLayout(axis_content_layout)
        axis_layout.addWidget(axis_group)
        axis_layout.addStretch()
        
        # Set up Button Mapping tab
        button_group = QGroupBox("Button Mapping Configuration")
        button_group.setFont(QFont("Roboto", 12, QFont.Weight.Bold))
        button_content_layout = QVBoxLayout()
        button_content_layout.setContentsMargins(20, 20, 20, 20)
        button_content_layout.setSpacing(15)
        
        # Add button mapping description
        button_label = QLabel(
            "Configure how your input device's buttons map to different actions.\n"
            "This allows you to customize the behavior of your device for optimal control."
        )
        button_label.setFont(QFont("Roboto", 10))
        button_label.setWordWrap(True)
        button_content_layout.addWidget(button_label)
        
        # Add headers for button mapping
        self.button_mapping_layout.addWidget(QLabel("Button"), 0, 0)
        self.button_mapping_layout.addWidget(QLabel("Function"), 0, 1)
        button_content_layout.addLayout(self.button_mapping_layout)
        
        # Add save/load buttons for button mapping
        button_button_layout = QHBoxLayout()
        button_save_btn = QPushButton("Save Button Mapping")
        button_save_btn.setIcon(qta.icon('fa5s.save', color='white'))
        button_save_btn.setFont(QFont("Roboto", 10))
        button_save_btn.clicked.connect(lambda: self.save_mapping("button"))
        
        button_load_btn = QPushButton("Load Button Mapping")
        button_load_btn.setIcon(qta.icon('fa5s.folder-open', color='white'))
        button_load_btn.setFont(QFont("Roboto", 10))
        button_load_btn.clicked.connect(lambda: self.load_mapping("button"))
        
        button_button_layout.addWidget(button_save_btn)
        button_button_layout.addWidget(button_load_btn)
        button_content_layout.addLayout(button_button_layout)
        
        button_group.setLayout(button_content_layout)
        button_layout.addWidget(button_group)
        button_layout.addStretch()
        
        # Add mapping tab widget to main layout
        layout.addWidget(mapping_tab_widget)
        
        # Set up mapping controls
        self.setup_mapping_controls()

    def setup_settings_tab(self, layout):
        """Set up the Settings tab content"""
        # Application Settings
        settings_group = QGroupBox("Application Settings")
        settings_group.setFont(QFont("Roboto", 12, QFont.Weight.Bold))
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_layout.setSpacing(15)
        
        # Add settings description
        settings_label = QLabel(
            "Configure theme and appearance"
        )
        settings_label.setFont(QFont("Roboto", 10))
        settings_label.setWordWrap(True)
        settings_layout.addWidget(settings_label)
        
        # Add theme selection
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()  # Store as instance variable
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText("Dark")  # Set default theme
        self.theme_combo.setFont(QFont("Roboto", 10))
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        theme_layout.addWidget(self.theme_combo)
        settings_layout.addLayout(theme_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        layout.addStretch()

    def apply_styling(self):
        """Apply consistent styling to the window"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2A2A2A;
            }
            QGroupBox {
                border: 1px solid #3A3A3A;
                border-radius: 8px;
                margin-top: 1.5em;
                padding: 20px;
                background-color: #333333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #F5F5F5;
            }
            QPushButton {
                background-color: #F28C38;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F39C48;
                border: 1px solid #F28C38;
            }
            QPushButton:pressed {
                background-color: #D67B27;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
            QComboBox {
                border: 1px solid #4A4A4A;
                border-radius: 6px;
                padding: 8px;
                background-color: #3A3A3A;
                color: #F5F5F5;
                min-width: 180px;
            }
            QComboBox:hover {
                border: 1px solid #F28C38;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QLabel {
                color: #F5F5F5;
            }
            QLineEdit {
                border: 1px solid #4A4A4A;
                border-radius: 6px;
                padding: 8px;
                background-color: #3A3A3A;
                color: #F5F5F5;
            }
            QLineEdit:hover {
                border: 1px solid #F28C38;
            }
            QTabWidget::pane {
                border: 1px solid #3A3A3A;
                border-radius: 8px;
                background-color: #333333;
            }
            QTabBar::tab {
                background-color: #2A2A2A;
                color: #F5F5F5;
                padding: 8px 20px;
                border: 1px solid #3A3A3A;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #F28C38;
                color: white;
                border: none;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3A3A3A;
            }
            QStatusBar {
                background-color: #333333;
                color: #F5F5F5;
            }
        """)

    def setup_gamepad(self):
        """Initialize pygame for gamepad support"""
        pygame.init()
        pygame.joystick.init()
        
        # Gamepad state and calibration
        self.gamepad = None
        self.is_reading_input = False
        self.input_timer = QTimer()
        self.input_timer.timeout.connect(self.read_gamepad_input)
        self.x_offset = 0.0
        self.y_offset = 0.0
        
        # Axis mapping flags
        self.x_mapping = False
        self.y_mapping = False
        self.z_mapping = False
        self.yaw_mapping = False
        self.pitch_mapping = False
        self.roll_mapping = False
        
    def load_config(self):
        """Load configuration from file"""
        try:
            with open("data/config.json", "r") as f:
                return json.load(f)
        except Exception as e:
            return {"udp": {"ip": "127.0.0.1", "port": 7755}}

    def update_device_list(self):
        """Update the device dropdown with available devices"""
        self.device_combo.clear()
        devices = self.lisu_manager.get_available_devices()
        for device in devices:
            self.device_combo.addItem(device["name"])
            
    def update_udp_target(self):
        """Update UDP target when IP or port changes"""
        try:
            ip = self.udp_ip.text()
            port = int(self.udp_port.text())
            self.lisu_manager.set_udp_target(ip, port)
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
                if self.lisu_manager.connect_device(device):
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
        """Control X-axis movement"""
        try:
            if self.gamepad:
                self.x_mapping = True
                self.y_mapping = False
                self.z_mapping = False
                self.status_bar.showMessage("Move controller to control X-axis movement")
            angle = float(self.rotation_input.text())
            cmd_type = self.cmd_combo.currentText()
            self.send_command(cmd_type, 1.0, 0.0, 0.0, angle)
        except ValueError:
            self.status_bar.showMessage("Invalid rotation angle value")
        except Exception as e:
            self.status_bar.showMessage(f"Error sending command: {str(e)}")
            
    def control_y_axis(self):
        """Control Y-axis movement"""
        try:
            if self.gamepad:
                self.x_mapping = False
                self.y_mapping = True
                self.z_mapping = False
                self.status_bar.showMessage("Move controller to control Y-axis movement")
            angle = float(self.rotation_input.text())
            cmd_type = self.cmd_combo.currentText()
            self.send_command(cmd_type, 0.0, 1.0, 0.0, angle)
        except ValueError:
            self.status_bar.showMessage("Invalid rotation angle value")
        except Exception as e:
            self.status_bar.showMessage(f"Error sending command: {str(e)}")
            
    def control_z_axis(self):
        """Control Z-axis movement"""
        try:
            if self.gamepad:
                self.x_mapping = False
                self.y_mapping = False
                self.z_mapping = True
                self.status_bar.showMessage("Move controller to control Z-axis movement")
            angle = float(self.rotation_input.text())
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
            step = float(self.step_input.text())
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
        """Apply light/dark theme"""
        theme = self.theme_combo.currentText()  # Use the instance variable instead of findChild
        if theme == "Dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2A2A2A;
                }
                QGroupBox {
                    border: 1px solid #3A3A3A;
                    border-radius: 8px;
                    margin-top: 1.5em;
                    padding: 20px;
                    background-color: #333333;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 10px;
                    color: #F5F5F5;
                }
                QPushButton {
                    background-color: #F28C38;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #F39C48;
                    border: 1px solid #F28C38;
                }
                QPushButton:pressed {
                    background-color: #D67B27;
                }
                QPushButton:disabled {
                    background-color: #666666;
                }
                QComboBox {
                    border: 1px solid #4A4A4A;
                    border-radius: 6px;
                    padding: 8px;
                    background-color: #3A3A3A;
                    color: #F5F5F5;
                    min-width: 180px;
                }
                QComboBox:hover {
                    border: 1px solid #F28C38;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    image: url(down_arrow.png);
                    width: 12px;
                    height: 12px;
                }
                QLabel {
                    color: #F5F5F5;
                }
                QLineEdit {
                    border: 1px solid #4A4A4A;
                    border-radius: 6px;
                    padding: 8px;
                    background-color: #3A3A3A;
                    color: #F5F5F5;
                }
                QLineEdit:hover {
                    border: 1px solid #F28C38;
                }
                QTabWidget::pane {
                    border: 1px solid #3A3A3A;
                    border-radius: 8px;
                    background-color: #333333;
                }
                QTabBar::tab {
                    background-color: #2A2A2A;
                    color: #F5F5F5;
                    padding: 8px 20px;
                    border: 1px solid #3A3A3A;
                    border-bottom: none;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                }
                QTabBar::tab:selected {
                    background-color: #F28C38;
                    color: white;
                    border: none;
                }
                QTabBar::tab:hover:!selected {
                    background-color: #3A3A3A;
                }
                QStatusBar {
                    background-color: #333333;
                    color: #F5F5F5;
                }
            """)
        else:  # Light theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #F5F5F5;
                }
                QGroupBox {
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    margin-top: 1.5em;
                    padding: 20px;
                    background-color: #FFFFFF;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 10px;
                    color: #333333;
                }
                QPushButton {
                    background-color: #F28C38;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #F39C48;
                    border: 1px solid #F28C38;
                }
                QPushButton:pressed {
                    background-color: #D67B27;
                }
                QPushButton:disabled {
                    background-color: #CCCCCC;
                }
                QComboBox {
                    border: 1px solid #E0E0E0;
                    border-radius: 6px;
                    padding: 8px;
                    background-color: #FFFFFF;
                    color: #333333;
                    min-width: 180px;
                }
                QComboBox:hover {
                    border: 1px solid #F28C38;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    image: url(down_arrow.png);
                    width: 12px;
                    height: 12px;
                }
                QLabel {
                    color: #333333;
                }
                QLineEdit {
                    border: 1px solid #E0E0E0;
                    border-radius: 6px;
                    padding: 8px;
                    background-color: #FFFFFF;
                    color: #333333;
                }
                QLineEdit:hover {
                    border: 1px solid #F28C38;
                }
                QTabWidget::pane {
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    background-color: #FFFFFF;
                }
                QTabBar::tab {
                    background-color: #F5F5F5;
                    color: #333333;
                    padding: 8px 20px;
                    border: 1px solid #E0E0E0;
                    border-bottom: none;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                }
                QTabBar::tab:selected {
                    background-color: #F28C38;
                    color: white;
                    border: none;
                }
                QTabBar::tab:hover:!selected {
                    background-color: #F0F0F0;
                }
                QStatusBar {
                    background-color: #FFFFFF;
                    color: #333333;
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
                        scale = float(self.rotation_input.text())
                        cmd_type = self.cmd_combo.currentText()
                        
                        # Map movement based on active axis
                        if self.x_mapping:
                            self.send_command(cmd_type, x_axis, 0.0, 0.0, scale)
                        elif self.y_mapping:
                            self.send_command(cmd_type, 0.0, -y_axis, 0.0, scale)
                        elif self.z_mapping:
                            self.send_command(cmd_type, 0.0, 0.0, -y_axis, scale)
                        elif self.yaw_mapping:
                            self.send_command(cmd_type, 0.0, x_axis, 0.0, scale)
                        elif self.pitch_mapping:
                            self.send_command(cmd_type, -y_axis, 0.0, 0.0, scale)
                        elif self.roll_mapping:
                            self.send_command(cmd_type, 0.0, 0.0, x_axis, scale)
                        else:
                            # Default behavior (no mapping active)
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

    def adjust_rotation(self, increment):
        """Adjust rotation angle by the specified increment"""
        try:
            current = float(self.rotation_input.text())
            new_angle = current + increment
            self.rotation_input.setText(str(new_angle))
        except ValueError:
            self.rotation_input.setText("40.0")

    def adjust_step(self, increment):
        """Adjust movement step by the specified increment"""
        try:
            current = float(self.step_input.text())
            new_step = current + increment
            self.step_input.setText(str(new_step))
        except ValueError:
            self.step_input.setText("1.0")

    def control_yaw(self):
        """Control Yaw rotation"""
        try:
            angle = float(self.rotation_input.text())
            cmd_type = self.cmd_combo.currentText()
            # Map current gamepad position to yaw axis
            if self.gamepad:
                self.yaw_mapping = True
                self.pitch_mapping = False
                self.roll_mapping = False
                self.status_bar.showMessage("Move controller to control Yaw rotation")
            self.send_command(cmd_type, 0.0, 1.0, 0.0, angle)  # Y-axis rotation for yaw
        except ValueError:
            self.status_bar.showMessage("Invalid rotation angle value")
        except Exception as e:
            self.status_bar.showMessage(f"Error sending command: {str(e)}")

    def control_pitch(self):
        """Control Pitch rotation"""
        try:
            angle = float(self.rotation_input.text())
            cmd_type = self.cmd_combo.currentText()
            # Map current gamepad position to pitch axis
            if self.gamepad:
                self.yaw_mapping = False
                self.pitch_mapping = True
                self.roll_mapping = False
                self.status_bar.showMessage("Move controller to control Pitch rotation")
            self.send_command(cmd_type, 1.0, 0.0, 0.0, angle)  # X-axis rotation for pitch
        except ValueError:
            self.status_bar.showMessage("Invalid rotation angle value")
        except Exception as e:
            self.status_bar.showMessage(f"Error sending command: {str(e)}")

    def control_roll(self):
        """Control Roll rotation"""
        try:
            angle = float(self.rotation_input.text())
            cmd_type = self.cmd_combo.currentText()
            # Map current gamepad position to roll axis
            if self.gamepad:
                self.yaw_mapping = False
                self.pitch_mapping = False
                self.roll_mapping = True
                self.status_bar.showMessage("Move controller to control Roll rotation")
            self.send_command(cmd_type, 0.0, 0.0, 1.0, angle)  # Z-axis rotation for roll
        except ValueError:
            self.status_bar.showMessage("Invalid rotation angle value")
        except Exception as e:
            self.status_bar.showMessage(f"Error sending command: {str(e)}")

    def setup_mapping_controls(self):
        """Set up the axis and button mapping controls based on device capabilities"""
        # Clear existing controls
        for control in self.axis_mapping_controls:
            self.axis_mapping_layout.removeWidget(control)
        self.axis_mapping_controls.clear()
        
        for control in self.button_mapping_controls:
            self.button_mapping_layout.removeWidget(control)
        self.button_mapping_controls.clear()
        
        # Get device capabilities
        try:
            device_type = self.device_type_combo.currentText()
            if device_type in self.device_capabilities:
                capabilities = self.device_capabilities[device_type]
                
                # Add axis mapping controls
                for i in range(capabilities["axes"]):
                    row = i + 1  # Start from row 1 (row 0 is header)
                    label = QLabel(f"Axis {i}:")
                    combo = QComboBox()
                    combo.addItems(["None", "X", "Y", "Z", "Yaw", "Pitch", "Roll"])
                    self.axis_mapping_layout.addWidget(label, row, 0)
                    self.axis_mapping_layout.addWidget(combo, row, 1)
                    self.axis_mapping_controls.append((label, combo))
                
                # Add button mapping controls
                for i in range(capabilities["buttons"]):
                    row = i + 1  # Start from row 1 (row 0 is header)
                    label = QLabel(f"Button {i}:")
                    combo = QComboBox()
                    combo.addItems(["None", "Move Forward", "Reset Position", "Calibrate"])
                    self.button_mapping_layout.addWidget(label, row, 0)
                    self.button_mapping_layout.addWidget(combo, row, 1)
                    self.button_mapping_controls.append((label, combo))
                
                self.status_bar.showMessage(f"Mapping controls set up for {device_type}")
            else:
                self.status_bar.showMessage(f"No capabilities defined for {device_type}")
        except Exception as e:
            print(f"Error setting up mapping controls: {e}")
            self.status_bar.showMessage(f"Error setting up mapping controls: {e}")
    
    def save_mapping(self, mapping_type):
        """Save the current axis or button mappings to configuration"""
        try:
            mapping_config = {
                "axis_mapping": {},
                "button_mapping": {}
            }
            
            if mapping_type == "axis":
                # Save axis mappings
                for i, (_, combo) in enumerate(self.axis_mapping_controls):
                    mapping_config["axis_mapping"][f"axis_{i}"] = combo.currentText()
                self.status_bar.showMessage("Axis mapping configuration saved successfully")
            elif mapping_type == "button":
                # Save button mappings
                for i, (_, combo) in enumerate(self.button_mapping_controls):
                    mapping_config["button_mapping"][f"button_{i}"] = combo.currentText()
                self.status_bar.showMessage("Button mapping configuration saved successfully")
            
            # Save to config file
            config_path = os.path.join(os.path.dirname(__file__), "..", "data", "mapping_config.json")
            with open(config_path, "w") as f:
                json.dump(mapping_config, f, indent=4)
                
        except Exception as e:
            self.status_bar.showMessage(f"Error saving {mapping_type} mapping: {e}")
    
    def load_mapping(self, mapping_type):
        """Load axis or button mappings from configuration"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "..", "data", "mapping_config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    mapping_config = json.load(f)
                
                if mapping_type == "axis":
                    # Load axis mappings
                    for i, (_, combo) in enumerate(self.axis_mapping_controls):
                        key = f"axis_{i}"
                        if key in mapping_config["axis_mapping"]:
                            index = combo.findText(mapping_config["axis_mapping"][key])
                            if index >= 0:
                                combo.setCurrentIndex(index)
                    self.status_bar.showMessage("Axis mapping configuration loaded successfully")
                elif mapping_type == "button":
                    # Load button mappings
                    for i, (_, combo) in enumerate(self.button_mapping_controls):
                        key = f"button_{i}"
                        if key in mapping_config["button_mapping"]:
                            index = combo.findText(mapping_config["button_mapping"][key])
                            if index >= 0:
                                combo.setCurrentIndex(index)
                    self.status_bar.showMessage("Button mapping configuration loaded successfully")
            else:
                self.status_bar.showMessage("No mapping configuration found")
        except Exception as e:
            self.status_bar.showMessage(f"Error loading {mapping_type} mapping: {e}")

    def on_device_selected(self, device_name):
        """Handle device selection"""
        self.selected_device = device_name
        self.setup_mapping_controls()  # Set up mapping controls when device is selected 

    def open_mapping_window(self):
        """Open the device mapping configuration window"""
        mapping_window = MappingWindow(self)
        mapping_window.exec() 