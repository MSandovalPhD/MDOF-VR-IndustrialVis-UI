from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QComboBox, QPushButton, QGroupBox,
                            QScrollArea, QWidget, QFrame, QToolTip)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon
import json
import os
import qtawesome as qta

class MappingWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Device Mapping Configuration")
        self.setMinimumSize(900, 700)
        
        # Create main layout with spacing
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Create scroll area for mappings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(25)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Device Selection with enhanced styling
        device_group = QGroupBox("Device Selection")
        device_group.setFont(QFont("Roboto", 14, QFont.Weight.Bold))
        device_layout = QHBoxLayout()
        device_layout.setContentsMargins(20, 20, 20, 20)
        device_layout.setSpacing(20)
        
        device_label = QLabel("Select Device:")
        device_label.setFont(QFont("Roboto", 12))
        self.device_combo = QComboBox()
        self.device_combo.setFont(QFont("Roboto", 12))
        self.device_combo.setMinimumWidth(250)
        self.device_combo.addItems(["Gamepad_0", "Bluetooth_mouse", "SpaceMouse"])
        self.device_combo.currentTextChanged.connect(self.on_device_selected)
        
        # Add device icon
        device_icon = qta.icon('fa5s.gamepad', color='#F28C38')
        device_icon_label = QLabel()
        device_icon_label.setPixmap(device_icon.pixmap(24, 24))
        
        device_layout.addWidget(device_icon_label)
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_combo)
        device_layout.addStretch()
        device_group.setLayout(device_layout)
        container_layout.addWidget(device_group)
        
        # Axis Mapping with enhanced styling
        axis_group = QGroupBox("Axis Mapping")
        axis_group.setFont(QFont("Roboto", 14, QFont.Weight.Bold))
        self.axis_layout = QGridLayout()
        self.axis_layout.setContentsMargins(20, 20, 20, 20)
        self.axis_layout.setSpacing(15)
        
        # Headers with enhanced styling
        headers = ["Axis", "Function", "Invert", "Sensitivity"]
        for col, header in enumerate(headers):
            label = QLabel(header)
            label.setFont(QFont("Roboto", 12, QFont.Weight.Bold))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #F28C38;")
            self.axis_layout.addWidget(label, 0, col)
        
        # Add separator line with accent color
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #F28C38;")
        self.axis_layout.addWidget(separator, 1, 0, 1, 4)
        
        self.axis_mapping_controls = []
        axis_group.setLayout(self.axis_layout)
        container_layout.addWidget(axis_group)
        
        # Button Mapping with enhanced styling
        button_group = QGroupBox("Button Mapping")
        button_group.setFont(QFont("Roboto", 14, QFont.Weight.Bold))
        self.button_layout = QGridLayout()
        self.button_layout.setContentsMargins(20, 20, 20, 20)
        self.button_layout.setSpacing(15)
        
        # Headers with enhanced styling
        button_headers = ["Button", "Function"]
        for col, header in enumerate(button_headers):
            label = QLabel(header)
            label.setFont(QFont("Roboto", 12, QFont.Weight.Bold))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #F28C38;")
            self.button_layout.addWidget(label, 0, col)
        
        # Add separator line with accent color
        button_separator = QFrame()
        button_separator.setFrameShape(QFrame.Shape.HLine)
        button_separator.setFrameShadow(QFrame.Shadow.Sunken)
        button_separator.setStyleSheet("background-color: #F28C38;")
        self.button_layout.addWidget(button_separator, 1, 0, 1, 2)
        
        self.button_mapping_controls = []
        button_group.setLayout(self.button_layout)
        container_layout.addWidget(button_group)
        
        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        # Bottom buttons with enhanced styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Create styled buttons with icons
        self.save_button = QPushButton("Save Configuration")
        self.save_button.setIcon(qta.icon('fa5s.save', color='white'))
        self.load_button = QPushButton("Load Configuration")
        self.load_button.setIcon(qta.icon('fa5s.folder-open', color='white'))
        self.close_button = QPushButton("Close")
        self.close_button.setIcon(qta.icon('fa5s.times', color='white'))
        
        # Style the buttons
        for button in [self.save_button, self.load_button, self.close_button]:
            button.setFont(QFont("Roboto", 12))
            button.setMinimumWidth(150)
            button.setMinimumHeight(40)
            button.setIconSize(QSize(16, 16))
        
        # Connect signals
        self.save_button.clicked.connect(self.save_mapping)
        self.load_button.clicked.connect(self.load_mapping)
        self.close_button.clicked.connect(self.accept)
        
        # Add buttons to layout
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.close_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Set up initial mappings
        self.setup_mapping_controls()
        
        # Apply styling
        self.apply_styling()
        
    def apply_styling(self):
        """Apply consistent styling to the window"""
        # Set window style
        self.setStyleSheet("""
            QDialog {
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
            QScrollArea {
                border: none;
            }
            QToolTip {
                background-color: #333333;
                color: #F5F5F5;
                border: 1px solid #F28C38;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        
    def setup_mapping_controls(self):
        """Set up the axis and button mapping controls based on device capabilities"""
        # Clear existing controls
        for control in self.axis_mapping_controls:
            for widget in control:
                self.axis_layout.removeWidget(widget)
        self.axis_mapping_controls.clear()
        
        for control in self.button_mapping_controls:
            for widget in control:
                self.button_layout.removeWidget(widget)
        self.button_mapping_controls.clear()
        
        # Get device capabilities (placeholder - replace with actual device detection)
        device = self.device_combo.currentText()
        if device == "Gamepad_0":
            num_axes = 4  # Example: 4 axes
            num_buttons = 8  # Example: 8 buttons
        else:
            num_axes = 2  # Example: 2 axes for mouse
            num_buttons = 3  # Example: 3 buttons for mouse
        
        # Add axis mapping controls
        for i in range(num_axes):
            row = i + 2  # Start from row 2 (row 0 is header, row 1 is separator)
            
            # Axis label with icon
            label = QLabel(f"Axis {i}")
            label.setFont(QFont("Roboto", 12))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Function combo with tooltip
            function_combo = QComboBox()
            function_combo.setFont(QFont("Roboto", 12))
            function_combo.addItems(["None", "X", "Y", "Z", "Yaw", "Pitch", "Roll"])
            function_combo.setToolTip("Select the function to map this axis to")
            
            # Invert combo with tooltip
            invert_check = QComboBox()
            invert_check.setFont(QFont("Roboto", 12))
            invert_check.addItems(["No", "Yes"])
            invert_check.setToolTip("Invert the axis direction")
            
            # Sensitivity combo with tooltip
            sensitivity = QComboBox()
            sensitivity.setFont(QFont("Roboto", 12))
            sensitivity.addItems(["0.5", "1.0", "1.5", "2.0"])
            sensitivity.setToolTip("Adjust the sensitivity of this axis")
            
            # Add widgets to layout
            self.axis_layout.addWidget(label, row, 0)
            self.axis_layout.addWidget(function_combo, row, 1)
            self.axis_layout.addWidget(invert_check, row, 2)
            self.axis_layout.addWidget(sensitivity, row, 3)
            
            self.axis_mapping_controls.append((label, function_combo, invert_check, sensitivity))
        
        # Add button mapping controls
        for i in range(num_buttons):
            row = i + 2  # Start from row 2 (row 0 is header, row 1 is separator)
            
            # Button label with icon
            label = QLabel(f"Button {i}")
            label.setFont(QFont("Roboto", 12))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Function combo with tooltip
            function_combo = QComboBox()
            function_combo.setFont(QFont("Roboto", 12))
            function_combo.addItems(["None", "Move Forward", "Reset Position", "Calibrate"])
            function_combo.setToolTip("Select the function to map this button to")
            
            # Add widgets to layout
            self.button_layout.addWidget(label, row, 0)
            self.button_layout.addWidget(function_combo, row, 1)
            
            self.button_mapping_controls.append((label, function_combo))
    
    def on_device_selected(self, device_name):
        """Handle device selection"""
        self.setup_mapping_controls()
    
    def save_mapping(self):
        """Save the current mapping configuration"""
        try:
            mapping_config = {
                "device": self.device_combo.currentText(),
                "axis_mapping": {},
                "button_mapping": {}
            }
            
            # Save axis mappings
            for i, (_, function_combo, invert_check, sensitivity) in enumerate(self.axis_mapping_controls):
                mapping_config["axis_mapping"][f"axis_{i}"] = {
                    "function": function_combo.currentText(),
                    "invert": invert_check.currentText() == "Yes",
                    "sensitivity": float(sensitivity.currentText())
                }
            
            # Save button mappings
            for i, (_, function_combo) in enumerate(self.button_mapping_controls):
                mapping_config["button_mapping"][f"button_{i}"] = function_combo.currentText()
            
            # Save to config file
            config_path = os.path.join(os.path.dirname(__file__), "..", "data", "mapping_config.json")
            with open(config_path, "w") as f:
                json.dump(mapping_config, f, indent=4)
            
            self.parent().status_bar.showMessage("Mapping configuration saved successfully")
        except Exception as e:
            self.parent().status_bar.showMessage(f"Error saving mapping: {e}")
    
    def load_mapping(self):
        """Load mapping configuration"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "..", "data", "mapping_config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    mapping_config = json.load(f)
                
                # Set device
                index = self.device_combo.findText(mapping_config.get("device", ""))
                if index >= 0:
                    self.device_combo.setCurrentIndex(index)
                
                # Load axis mappings
                for i, (_, function_combo, invert_check, sensitivity) in enumerate(self.axis_mapping_controls):
                    key = f"axis_{i}"
                    if key in mapping_config["axis_mapping"]:
                        axis_config = mapping_config["axis_mapping"][key]
                        function_combo.setCurrentText(axis_config["function"])
                        invert_check.setCurrentText("Yes" if axis_config["invert"] else "No")
                        sensitivity.setCurrentText(str(axis_config["sensitivity"]))
                
                # Load button mappings
                for i, (_, function_combo) in enumerate(self.button_mapping_controls):
                    key = f"button_{i}"
                    if key in mapping_config["button_mapping"]:
                        function_combo.setCurrentText(mapping_config["button_mapping"][key])
                
                self.parent().status_bar.showMessage("Mapping configuration loaded successfully")
            else:
                self.parent().status_bar.showMessage("No mapping configuration found")
        except Exception as e:
            self.parent().status_bar.showMessage(f"Error loading mapping: {e}") 