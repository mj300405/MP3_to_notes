# main.py
import sys
from PySide6.QtWidgets import QApplication
from window import SoundToNotesApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = SoundToNotesApp()
    mainWindow.show()
    sys.exit(app.exec())
