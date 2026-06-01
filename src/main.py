"""
Main entry point for the English Fluency Coach application.
Initializes the UI and ties together the components.
"""

import sys
import os
import traceback

# Determine base directory immediately
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Standard Output Redirection
log_path = os.path.join(base_dir, "startup_debug.txt")
try:
    log_file = open(log_path, "w", encoding="utf-8")
    sys.stdout = log_file
    sys.stderr = log_file
except Exception:
    pass

# Safe Launch Block
try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from views.ui import FluencyCoachMainWindow

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        crash_log_path = os.path.join(base_dir, "crash_log.txt")
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        try:
            with open(crash_log_path, "a", encoding="utf-8") as f:
                f.write("CRITICAL CRASH:\n")
                f.write(error_msg)
                f.write("\n" + "="*50 + "\n")
        except:
            pass
            
        try:
            app = QApplication.instance()
            if not app:
                app = QApplication(sys.argv)
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Critical Error")
            msg_box.setText("A critical error occurred and the application must close.")
            msg_box.setDetailedText(error_msg)
            msg_box.exec()
        except:
            pass
            
        sys.exit(1)

    sys.excepthook = handle_exception

    def main():
        app = QApplication(sys.argv)
        
        window = FluencyCoachMainWindow()
        window.show()
        
        sys.exit(app.exec())

    if __name__ == "__main__":
        main()

except Exception:
    error_msg = traceback.format_exc()
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\nFATAL BOOT ERROR:\n")
            f.write(error_msg)
            f.write("\n")
    except:
        pass
    sys.exit(1)
