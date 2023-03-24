import sys
from PyQt5.QtWidgets import QApplication
from welcome_window import WelcomeWindow
from app import Application

import warnings
warnings.simplefilter('ignore')

import settings
settings.init()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome_app = Application()
    window = WelcomeWindow(welcome_app)
    sys.exit(app.exec())