from PyQt5.QtWidgets import QWidget, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QGridLayout, QListWidget, QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import matplotlib.container
import os

class SidePanelWindow(QWidget):
    """
    Side panel window for settings.
    """
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 300, 800)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "Logo_NBackground.png")
        self.setWindowIcon(QIcon(icon_path))

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.init_model_settings_ui()
        self.init_plot_settings_ui()
        self.init_correction_settings_ui()
        self.init_line_settings_ui()

        self.show_model_settings()

    def init_model_settings_ui(self):
        """
        Initialize UI elements for model settings.
        """
        self.left_arrow_button = QPushButton("←")
        self.left_arrow_button.clicked.connect(self.show_plot_settings)
        self.layout.addWidget(self.left_arrow_button, 0, 0)

        self.right_arrow_button = QPushButton("→")
        self.right_arrow_button.clicked.connect(self.show_plot_settings)
        self.layout.addWidget(self.right_arrow_button, 0, 2)

        self.title_section1 = QLabel("📈 Model Settings")
        self.title_section1.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_section1, 0, 1)

        self.model_combo = QComboBox()
        self.model_combo.addItems(["SARIMAX", "ARIMAX", "ARIMA"])
        self.model_combo.currentTextChanged.connect(self.update_model_parameters)
        self.layout.addWidget(self.model_combo, 1, 0, 1, 3)

        self.p_range_label = QLabel("p_range :")
        self.layout.addWidget(self.p_range_label, 2, 0)
        self.p_range_input = QLineEdit("0,2")
        self.layout.addWidget(self.p_range_input, 2, 1, 1, 2)

        self.d_range_label = QLabel("d_range :")
        self.layout.addWidget(self.d_range_label, 3, 0)
        self.d_range_input = QLineEdit("0,2")
        self.layout.addWidget(self.d_range_input, 3, 1, 1, 2)

        self.q_range_label = QLabel("q_range :")
        self.layout.addWidget(self.q_range_label, 4, 0)
        self.q_range_input = QLineEdit("0,2")
        self.layout.addWidget(self.q_range_input, 4, 1, 1, 2)

        self.seasonal_period_label = QLabel("Seasonality :")
        self.layout.addWidget(self.seasonal_period_label, 5, 0)
        self.seasonal_period_input = QLineEdit("12")
        self.layout.addWidget(self.seasonal_period_input, 5, 1, 1, 2)

        self.forecast_until_label = QLabel("Forecast year:")
        self.layout.addWidget(self.forecast_until_label, 6, 0)
        self.forecast_until_input = QLineEdit("2100")
        self.layout.addWidget(self.forecast_until_input, 6, 1, 1, 2)

        self.replace_negative_forecast_checkbox = QCheckBox("0 values")
        self.layout.addWidget(self.replace_negative_forecast_checkbox, 7, 0, 1, 3)

        self.show_confidence_interval_checkbox = QCheckBox("Show Confidence Interval")
        self.layout.addWidget(self.show_confidence_interval_checkbox, 8, 0, 1, 3)

        self.apply_button = QPushButton("Apply Settings")
        self.apply_button.clicked.connect(self.apply_model)
        self.layout.addWidget(self.apply_button, 9, 0, 1, 3)

    def init_plot_settings_ui(self):
        """
        Initialize UI elements for plot settings.
        """
        self.left_arrow_button2 = QPushButton("←")
        self.left_arrow_button2.clicked.connect(self.show_model_settings)
        self.left_arrow_button2.setVisible(False)
        self.layout.addWidget(self.left_arrow_button2, 0, 0)

        self.right_arrow_button2 = QPushButton("→")
        self.right_arrow_button2.clicked.connect(self.show_model_settings)
        self.right_arrow_button2.setVisible(False)
        self.layout.addWidget(self.right_arrow_button2, 0, 2)

        self.title_section2 = QLabel("📊 Plot Settings")
        self.title_section2.setAlignment(Qt.AlignCenter)
        self.title_section2.setVisible(False)
        self.layout.addWidget(self.title_section2, 0, 1)

        self.x_axis_label = QLabel("X-axis :")
        self.x_axis_label.setVisible(False)
        self.layout.addWidget(self.x_axis_label, 1, 0)
        self.x_axis_input = QLineEdit("0,2100")
        self.x_axis_input.setVisible(False)
        self.layout.addWidget(self.x_axis_input, 1, 1, 1, 2)

        self.y_axis_label = QLabel("Y-axis :")
        self.y_axis_label.setVisible(False)
        self.layout.addWidget(self.y_axis_label, 2, 0)
        self.y_axis_input = QLineEdit("0,100")
        self.y_axis_input.setVisible(False)
        self.layout.addWidget(self.y_axis_input, 2, 1, 1, 2)

        self.title_label = QLabel("Chart Title:")
        self.title_label.setVisible(False)
        self.layout.addWidget(self.title_label, 3, 0)
        self.title_input = QLineEdit("Chart Title")
        self.title_input.setVisible(False)
        self.layout.addWidget(self.title_input, 3, 1, 1, 2)

        self.legend_size_label = QLabel("Legend Size:")
        self.legend_size_label.setVisible(False)
        self.layout.addWidget(self.legend_size_label, 4, 0)
        self.legend_size_input = QLineEdit("10")
        self.legend_size_input.setVisible(False)
        self.layout.addWidget(self.legend_size_input, 4, 1, 1, 2)

        self.legend_position_label = QLabel("Legend Position:")
        self.legend_position_label.setVisible(False)
        self.layout.addWidget(self.legend_position_label, 5, 0)
        self.legend_position_combo = QComboBox()
        self.legend_position_combo.addItems(["Upper Left", "Bottom Left", "Upper Right", "Bottom Right"])
        self.legend_position_combo.setVisible(False)
        self.layout.addWidget(self.legend_position_combo, 5, 1, 1, 2)

        self.ylabel_label = QLabel("Y-axis Label:")
        self.ylabel_label.setVisible(False)
        self.layout.addWidget(self.ylabel_label, 6, 0)
        self.ylabel_input = QLineEdit("Y-axis Label")
        self.ylabel_input.setVisible(False)
        self.layout.addWidget(self.ylabel_input, 6, 1, 1, 2)

        self.xlabel_label = QLabel("X-axis Label:")
        self.xlabel_label.setVisible(False)
        self.layout.addWidget(self.xlabel_label, 7, 0)
        self.xlabel_input = QLineEdit("X-axis Label")
        self.xlabel_input.setVisible(False)
        self.layout.addWidget(self.xlabel_input, 7, 1, 1, 2)

        self.ylabel_size_label = QLabel("Y-axis Label Size:")
        self.ylabel_size_label.setVisible(False)
        self.layout.addWidget(self.ylabel_size_label, 8, 0)
        self.ylabel_size_input = QLineEdit("14")
        self.ylabel_size_input.setVisible(False)
        self.layout.addWidget(self.ylabel_size_input, 8, 1, 1, 2)

        self.xlabel_size_label = QLabel("X-axis Label Size:")
        self.xlabel_size_label.setVisible(False)
        self.layout.addWidget(self.xlabel_size_label, 9, 0)
        self.xlabel_size_input = QLineEdit("14")
        self.xlabel_size_input.setVisible(False)
        self.layout.addWidget(self.xlabel_size_input, 9, 1, 1, 2)

        self.apply_plot_button = QPushButton("Apply Plot Settings")
        self.apply_plot_button.clicked.connect(self.apply_plot_settings)
        self.apply_plot_button.setVisible(False)
        self.layout.addWidget(self.apply_plot_button, 10, 0, 1, 3)

    def show_model_settings(self):
        """
        Show the model settings UI elements.
        """
        self.title_section1.setVisible(True)
        self.left_arrow_button.setVisible(True)
        self.right_arrow_button.setVisible(True)
        self.model_combo.setVisible(True)
        self.p_range_label.setVisible(True)
        self.p_range_input.setVisible(True)
        self.d_range_label.setVisible(True)
        self.d_range_input.setVisible(True)
        self.q_range_label.setVisible(True)
        self.q_range_input.setVisible(True)
        self.seasonal_period_label.setVisible(self.model_combo.currentText() == "SARIMAX")
        self.seasonal_period_input.setVisible(self.model_combo.currentText() == "SARIMAX")
        self.forecast_until_label.setVisible(True)
        self.forecast_until_input.setVisible(True)
        self.replace_negative_forecast_checkbox.setVisible(True)
        self.show_confidence_interval_checkbox.setVisible(True)
        self.target_year_label.setVisible(True)
        self.target_year_input.setVisible(True)
        self.target_value_label.setVisible(True)
        self.target_value_input.setVisible(True)
        self.continuous_correction_checkbox.setVisible(True)
        self.short_correction_checkbox.setVisible(True)
        self.start_correction_checkbox.setVisible(True)
        self.apply_correction_button.setVisible(True)
        self.apply_button.setVisible(True)
        self.start_target_year_label.setVisible(True)
        self.start_target_year_input.setVisible(True)        

        self.title_section2.setVisible(False)
        self.left_arrow_button2.setVisible(False)
        self.right_arrow_button2.setVisible(False)
        self.x_axis_label.setVisible(False)
        self.x_axis_input.setVisible(False)
        self.y_axis_label.setVisible(False)
        self.y_axis_input.setVisible(False)
        self.title_label.setVisible(False)
        self.title_input.setVisible(False)
        self.legend_size_label.setVisible(False)
        self.legend_size_input.setVisible(False)
        self.legend_position_label.setVisible(False)
        self.legend_position_combo.setVisible(False)
        self.ylabel_label.setVisible(False)
        self.ylabel_input.setVisible(False)
        self.xlabel_label.setVisible(False)
        self.xlabel_input.setVisible(False)
        self.ylabel_size_label.setVisible(False)
        self.ylabel_size_input.setVisible(False)
        self.xlabel_size_label.setVisible(False)
        self.xlabel_size_input.setVisible(False)
        self.apply_plot_button.setVisible(False)
        self.line_list_label.setVisible(False)
        self.line_list.setVisible(False)
        self.new_line_label.setVisible(False)
        self.line_name_label.setVisible(False)
        self.line_name_input.setVisible(False)
        self.line_value_label.setVisible(False)
        self.line_value_input.setVisible(False)
        self.line_color_label.setVisible(False)
        self.line_color_combo.setVisible(False)
        self.line_type_label.setVisible(False)
        self.line_type_combo.setVisible(False)
        self.add_line_button.setVisible(False)
        self.line_axis_label.setVisible(False)
        self.line_axis_combo.setVisible(False)
        self.line_type_combo.setVisible(False)

    def show_plot_settings(self):
        """
        Show the plot settings UI elements.
        """
        self.title_section1.setVisible(False)
        self.left_arrow_button.setVisible(False)
        self.right_arrow_button.setVisible(False)
        self.model_combo.setVisible(False)
        self.p_range_label.setVisible(False)
        self.p_range_input.setVisible(False)
        self.d_range_label.setVisible(False)
        self.d_range_input.setVisible(False)
        self.q_range_label.setVisible(False)
        self.q_range_input.setVisible(False)
        self.seasonal_period_label.setVisible(False)
        self.seasonal_period_input.setVisible(False)
        self.forecast_until_label.setVisible(False)
        self.forecast_until_input.setVisible(False)
        self.replace_negative_forecast_checkbox.setVisible(False)
        self.show_confidence_interval_checkbox.setVisible(False)
        self.target_year_label.setVisible(False)
        self.target_year_input.setVisible(False)
        self.target_value_label.setVisible(False)
        self.target_value_input.setVisible(False)
        self.continuous_correction_checkbox.setVisible(False)
        self.short_correction_checkbox.setVisible(False)
        self.start_correction_checkbox.setVisible(False)
        self.apply_correction_button.setVisible(False)
        self.apply_button.setVisible(False)
        self.start_target_year_label.setVisible(False)
        self.start_target_year_input.setVisible(False)        

        self.title_section2.setVisible(True)
        self.left_arrow_button2.setVisible(True)
        self.right_arrow_button2.setVisible(True)
        self.x_axis_label.setVisible(True)
        self.x_axis_input.setVisible(True)
        self.y_axis_label.setVisible(True)
        self.y_axis_input.setVisible(True)
        self.title_label.setVisible(True)
        self.title_input.setVisible(True)
        self.legend_size_label.setVisible(True)
        self.legend_size_input.setVisible(True)
        self.legend_position_label.setVisible(True)
        self.legend_position_combo.setVisible(True)
        self.ylabel_label.setVisible(True)
        self.ylabel_input.setVisible(True)
        self.xlabel_label.setVisible(True)
        self.xlabel_input.setVisible(True)
        self.ylabel_size_label.setVisible(True)
        self.ylabel_size_input.setVisible(True)
        self.xlabel_size_label.setVisible(True)
        self.xlabel_size_input.setVisible(True)
        self.apply_plot_button.setVisible(True)
        self.line_list_label.setVisible(True)
        self.line_list.setVisible(True)
        self.new_line_label.setVisible(True)
        self.line_name_label.setVisible(True)
        self.line_name_input.setVisible(True)
        self.line_value_label.setVisible(True)
        self.line_value_input.setVisible(True)
        self.line_color_label.setVisible(True)
        self.line_color_combo.setVisible(True)
        self.line_type_label.setVisible(True)
        self.line_type_combo.setVisible(True)
        self.add_line_button.setVisible(True)
        self.line_axis_label.setVisible(True)
        self.line_axis_combo.setVisible(True)
        self.line_type_combo.setVisible(True)

    def update_model_parameters(self, model_name):
        """
        Update model parameters based on selected model.

        Args:
            model_name (str): The name of the model.
        """
        is_sarimax = model_name == "SARIMAX"
        is_arimax = model_name == "ARIMAX"
        is_arima = model_name == "ARIMA"
        self.p_range_label.setVisible(is_sarimax or is_arimax or is_arima)
        self.p_range_input.setVisible(is_sarimax or is_arimax or is_arima)
        self.d_range_label.setVisible(is_sarimax or is_arimax or is_arima)
        self.d_range_input.setVisible(is_sarimax or is_arimax or is_arima)
        self.q_range_label.setVisible(is_sarimax or is_arimax or is_arima)
        self.q_range_input.setVisible(is_sarimax or is_arimax or is_arima)
        self.seasonal_period_label.setVisible(is_sarimax)
        self.seasonal_period_input.setVisible(is_sarimax)
        self.forecast_until_label.setVisible(is_sarimax or is_arimax or is_arima)
        self.forecast_until_input.setVisible(is_sarimax or is_arimax or is_arima)
        self.replace_negative_forecast_checkbox.setVisible(is_sarimax or is_arimax or is_arima)

    def apply_model(self):
        """
        Apply the selected model settings.
        """
        model_name = self.model_combo.currentText()
        if model_name == "SARIMAX":
            self.apply_sarimax()
        elif model_name == "ARIMAX":
            self.apply_arimax()
        elif model_name == "ARIMA":
            self.apply_arima()

    def apply_sarimax(self):
        """
        Apply SARIMAX model settings.
        """
        p_range = self.get_range(self.p_range_input.text(), [0, 2])
        d_range = self.get_range(self.d_range_input.text(), [0, 2])
        q_range = self.get_range(self.q_range_input.text(), [0, 2])
        seasonal_period = int(self.seasonal_period_input.text()) if self.seasonal_period_input.text() else 11

        forecast_until_year = int(self.forecast_until_input.text()) if self.forecast_until_input.text() else 2100
        self.main_window.forecast_until_year = forecast_until_year

        self.main_window.replace_negative_forecast = self.replace_negative_forecast_checkbox.isChecked()

        self.main_window.run_sarimax(p_range, d_range, q_range, seasonal_period)

    def apply_arimax(self):
        """
        Apply ARIMAX model settings.
        """
        p_range = self.get_range(self.p_range_input.text(), [0, 2])
        d_range = self.get_range(self.d_range_input.text(), [0, 2])
        q_range = self.get_range(self.q_range_input.text(), [0, 2])

        forecast_until_year = int(self.forecast_until_input.text()) if self.forecast_until_input.text() else 2100
        self.main_window.forecast_until_year = forecast_until_year

        self.main_window.replace_negative_forecast = self.replace_negative_forecast_checkbox.isChecked()

        self.main_window.run_arimax(p_range, d_range, q_range)

    def apply_arima(self):
        """
        Apply ARIMA model settings.
        """
        p_range = self.get_range(self.p_range_input.text(), [0, 2])
        d_range = self.get_range(self.d_range_input.text(), [0, 2])
        q_range = self.get_range(self.q_range_input.text(), [0, 2])

        forecast_until_year = int(self.forecast_until_input.text()) if self.forecast_until_input.text() else 2100
        self.main_window.forecast_until_year = forecast_until_year

        self.main_window.replace_negative_forecast = self.replace_negative_forecast_checkbox.isChecked()

        self.main_window.run_arima(p_range, d_range, q_range)

    def get_range(self, text, default):
        """
        Get a range of values from a text input.

        Args:
            text (str): The text input.
            default (list): The default range.

        Returns:
            list: The range of values.
        """
        if text:
            try:
                values = list(map(int, text.split(',')))
                if len(values) == 2:
                    return values
                else:
                    return default
            except ValueError:
                return default
        else:
            return default

    def apply_plot_settings(self):
        """
        Apply the plot settings and update the graph with selected lines.
        """
        # Apply plot settings
        x_range = self.get_range(self.x_axis_input.text(), None)
        y_range = self.get_range(self.y_axis_input.text(), None)
        title = self.title_input.text()
        legend_size = int(self.legend_size_input.text()) if self.legend_size_input.text() else None
        legend_position = self.legend_position_combo.currentText().replace(" ", "").lower()
        xlabel = self.xlabel_input.text()
        ylabel = self.ylabel_input.text()
        xlabel_size = int(self.xlabel_size_input.text()) if self.xlabel_size_input.text() else None
        ylabel_size = int(self.ylabel_size_input.text()) if self.ylabel_size_input.text() else None

        self.main_window.apply_plot_settings(x_range, y_range, title, legend_size, legend_position, xlabel, ylabel, xlabel_size, ylabel_size)

        for index in range(self.line_list.count()):
            item = self.line_list.item(index)
            line_name = item.text()
            for line in self.main_window.active_lines:
                if line['name'] == line_name:
                    line['active'] = item.checkState() == Qt.Checked

        self.clear_lines()
        self.draw_lines()
        self.update_legend()

    def init_correction_settings_ui(self):
        """
        Initialize UI elements for correction settings.
        """
        self.target_year_label = QLabel("Target Year:")
        self.layout.addWidget(self.target_year_label, 10, 0)
        self.target_year_input = QLineEdit("")
        self.layout.addWidget(self.target_year_input, 10, 1, 1, 2)

        self.start_target_year_label = QLabel("Start Target Year:") 
        self.layout.addWidget(self.start_target_year_label, 11, 0)
        self.start_target_year_input = QLineEdit("")
        self.layout.addWidget(self.start_target_year_input, 11, 1, 1, 2)

        self.target_value_label = QLabel("Target Value:")
        self.layout.addWidget(self.target_value_label, 12, 0)
        self.target_value_input = QLineEdit("")
        self.layout.addWidget(self.target_value_input, 12, 1, 1, 2)

        self.continuous_correction_checkbox = QCheckBox("Continuous Correction")
        self.layout.addWidget(self.continuous_correction_checkbox, 13, 0, 1, 3)

        self.short_correction_checkbox = QCheckBox("Short Correction")
        self.layout.addWidget(self.short_correction_checkbox, 14, 0, 1, 3)

        self.start_correction_checkbox = QCheckBox("Start Correction")
        self.layout.addWidget(self.start_correction_checkbox, 15, 0, 1, 3)

        self.apply_correction_button = QPushButton("Apply Correction")
        self.apply_correction_button.clicked.connect(self.main_window.apply_forecast_corrections)
        self.layout.addWidget(self.apply_correction_button, 16, 0, 1, 3)

    def init_line_settings_ui(self):
        """
        Initialize UI elements for line settings.
        """
        self.line_list_label = QLabel("Active Lines:")
        self.layout.addWidget(self.line_list_label, 17, 0)
        self.line_list = QListWidget()
        self.update_line_list()
        self.layout.addWidget(self.line_list, 18, 0, 1, 3)

        self.new_line_label = QLabel("Add New Line:")
        self.layout.addWidget(self.new_line_label, 19, 0)
        self.line_name_label = QLabel("Name:")
        self.layout.addWidget(self.line_name_label, 20, 0)
        self.line_name_input = QLineEdit()
        self.layout.addWidget(self.line_name_input, 20, 1, 1, 2)

        self.line_value_label = QLabel("Value:")
        self.layout.addWidget(self.line_value_label, 21, 0)
        self.line_value_input = QLineEdit()
        self.layout.addWidget(self.line_value_input, 21, 1, 1, 2)

        self.line_color_label = QLabel("Color:")
        self.layout.addWidget(self.line_color_label, 22, 0)
        self.line_color_combo = QComboBox()
        self.line_color_combo.addItems(["red", "blue", "green", "yellow", "black"])
        self.layout.addWidget(self.line_color_combo, 22, 1, 1, 2)

        self.line_axis_label = QLabel("Axis:")
        self.layout.addWidget(self.line_axis_label, 23, 0)
        self.line_axis_combo = QComboBox()
        self.line_axis_combo.addItems(["x-axis", "y-axis"])
        self.layout.addWidget(self.line_axis_combo, 23, 1, 1, 2)

        self.line_type_label = QLabel("Type:")
        self.layout.addWidget(self.line_type_label, 24, 0)
        self.line_type_combo = QComboBox()
        self.line_type_combo.addItems(["solid", "dashed", "dotted"])
        self.layout.addWidget(self.line_type_combo, 24, 1, 1, 2)

        self.add_line_button = QPushButton("Add Line")
        self.add_line_button.clicked.connect(self.add_line)
        self.layout.addWidget(self.add_line_button, 25, 0, 1, 3)

    def update_line_list(self):
        """
        Update the list of active lines.
        """
        self.line_list.clear()
        for line in self.main_window.active_lines:
            item = QListWidgetItem(line['name'])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if line['active'] else Qt.Unchecked)
            self.line_list.addItem(item)

    def add_line(self):
        """
        Add a line to the plot based on the user input.
        """
        name = self.line_name_input.text()
        value = self.line_value_input.text()
        color = self.line_color_combo.currentText()
        line_type = self.line_type_combo.currentText()
        axis = self.line_axis_combo.currentText()

        try:
            value = float(value)
            line = {'name': name, 'value': value, 'color': color, 'type': line_type, 'axis': axis, 'active': True}
            self.main_window.active_lines.append(line)
            self.main_window.console.append(f"Added line: {line}")
            self.update_line_list()
        except ValueError:
            self.main_window.console.append("Invalid value for the line.")
                  
    def draw_lines(self):
        """
        Draw the active lines on the plot.
        """
        ax = self.main_window.canvas.figure.gca()
        for line in self.main_window.active_lines:
            if line['active']:
                linestyle = '-' if line['type'] == 'solid' else '--' if line['type'] == 'dashed' else ':'
                if line['axis'] == 'x-axis':
                    ax.axvline(x=line['value'], color=line['color'], linestyle=linestyle, label=line['name'])
                else:
                    ax.axhline(y=line['value'], color=line['color'], linestyle=linestyle, label=line['name'])
                ax.lines[-1].set_visible(True)
        self.main_window.canvas.draw()
        
    def clear_lines(self):
        """
        Hide all lines from the plot added by the SidePanel.
        """
        ax = self.main_window.canvas.figure.gca()
        for line in ax.get_lines():
            if line.get_label() in [l['name'] for l in self.main_window.active_lines]:
                line.set_visible(False)
        self.main_window.canvas.draw()
        
    def update_legend(self):
        """
        Update the legend to reflect the current active lines.
        """
        ax = self.main_window.canvas.figure.gca()
        handles, labels = ax.get_legend_handles_labels()
        visible_handles_labels = []
        for handle, label in zip(handles, labels):
            if isinstance(handle, matplotlib.container.BarContainer):
                if any(bar.get_visible() for bar in handle.get_children()):
                    visible_handles_labels.append((handle, label))
            else:
                if handle.get_visible():
                    visible_handles_labels.append((handle, label))

        if visible_handles_labels:
            handles, labels = zip(*visible_handles_labels)
            ax.legend(handles, labels)
        else:
            ax.legend().remove()
        self.main_window.canvas.draw()
