"""
© Mario Sandoval Olive 2024. All rights reserved.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from lisu.lisu_handler import LisuManager

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Create LISU manager
    lisu_manager = LisuManager()
    
    # Create and show main window
    window = MainWindow(lisu_manager)
    window.show()
    
    # Start application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 