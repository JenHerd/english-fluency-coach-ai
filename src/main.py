"""
Main entry point for the English Fluency Coach application.
Initializes the UI and ties together the components.
"""

import sys
from PyQt6.QtWidgets import QApplication
from views.ui import FluencyCoachMainWindow

def main():
    app = QApplication(sys.argv)
    
    window = FluencyCoachMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
