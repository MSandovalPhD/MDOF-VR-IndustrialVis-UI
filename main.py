import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from lisu.lisu_handler import LisuManager

def main():
    # Initialize the LISU framework
    lisu = LisuManager()
    
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = MainWindow(lisu)
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 