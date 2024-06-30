from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog
from PyQt5.QtGui import QIcon
import os

class SaveDialog(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.setWindowTitle("Save Data")
        self.setGeometry(100, 100, 300, 200)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "Logo_NBackground.png")
        self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout()

        self.save_type_label = QLabel("Select data type to save:", self)
        layout.addWidget(self.save_type_label)

        self.save_type_combo = QComboBox(self)
        self.save_type_combo.addItems(["Historical", "Forecast", "Both"])
        layout.addWidget(self.save_type_combo)

        self.format_label = QLabel("Select format to save:", self)
        layout.addWidget(self.format_label)

        self.format_combo = QComboBox(self)
        self.format_combo.addItems(["Format 1 (Original)", "Format 2 (New)"])
        layout.addWidget(self.format_combo)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_data)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_data(self):
        save_type = self.save_type_combo.currentText()
        format_type = self.format_combo.currentText()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", self.main_window.extracted_dataset_dir, "CSV Files (*.csv);;All Files (*)")
        if save_path:
            self.main_window.save_forecast(save_type, format_type, save_path)
            self.close()
