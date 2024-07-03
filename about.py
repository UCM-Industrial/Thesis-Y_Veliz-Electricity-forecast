from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon
import os

class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        self.setGeometry(100, 100, 300, 200)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "Logo_NBackground.png")
        self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout()

        about_label = QLabel("Forecasting Application\nVersion Alpha 1.0\nContact: yerko.veliz@alu.ucm.cl", self)
        layout.addWidget(about_label)

        self.setLayout(layout)
