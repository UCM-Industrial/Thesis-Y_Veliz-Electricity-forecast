import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QComboBox, QTextEdit, QFileDialog, QLabel, QSpinBox, QListWidget, QListWidgetItem, QLineEdit, QGridLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from Adf_test import perform_adf_test_with_differencing
from Sarimax import optimize_sarimax_models, forecast_future as forecast_future_sarimax
from Arimax import optimize_arimax_models, forecast_future as forecast_future_arimax
from Arima import optimize_arima_models, forecast_future as forecast_future_arima
from Plotting import plot_data, plot_data_stacked_bar, plot_historical_data, plot_historical_data_bar
from SidePanel import SidePanelWindow
from GroupPanel import GroupPanelWindow
from SavePanel import SaveDialog

class MainWindow(QMainWindow):
    """
    Main application window for forecasting.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Forecasting")
        self.setGeometry(100, 100, 940, 880)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "Logo_NBackground.png")
        self.setWindowIcon(QIcon(icon_path))

        self.dataset_dir = os.path.join(script_dir, "dataset")
        self.extracted_dataset_dir = os.path.join(script_dir, "extracted_dataset")
        self.plot_dir = os.path.join(script_dir, "plot")

        os.makedirs(self.dataset_dir, exist_ok=True)
        os.makedirs(self.extracted_dataset_dir, exist_ok=True)
        os.makedirs(self.plot_dir, exist_ok=True)

        container = QWidget()
        self.setCentralWidget(container)

        layout = QGridLayout(container)

        self.load_button = QPushButton("📁")
        self.load_button.clicked.connect(self.load_file)
        self.load_button.setFixedSize(30, 30)
        layout.addWidget(self.load_button, 0, 0)

        self.save_button = QPushButton("💾")
        self.save_button.clicked.connect(self.show_save_dialog)
        self.save_button.setFixedSize(30, 30)
        layout.addWidget(self.save_button, 0, 1)

        self.toggleSidePanelButton = QPushButton("⚙️")
        self.toggleSidePanelButton.clicked.connect(self.toggleSidePanel)
        self.toggleSidePanelButton.setFixedSize(30, 30)
        layout.addWidget(self.toggleSidePanelButton, 0, 2)

        self.clear_button = QPushButton("🗑️")
        self.clear_button.clicked.connect(self.clear_all)
        self.clear_button.setFixedSize(30, 30)
        layout.addWidget(self.clear_button, 0, 3)

        self.country_search = QLineEdit()
        self.country_search.setPlaceholderText("Search country...")
        layout.addWidget(self.country_search, 1, 0, 1, 4)
        self.country_search.textChanged.connect(self.filter_country_list)

        self.country_list = QListWidget()
        layout.addWidget(self.country_list, 2, 0, 1, 4)

        self.variable_combo = QComboBox()
        layout.addWidget(self.variable_combo, 1, 4, 1, 2)

        self.forecasted_country_search = QLineEdit()
        self.forecasted_country_search.setPlaceholderText("Search forecast country...")
        layout.addWidget(self.forecasted_country_search, 1, 6, 1, 4)
        self.forecasted_country_search.textChanged.connect(self.filter_forecasted_country_list)

        self.forecasted_country_list = QListWidget()
        layout.addWidget(self.forecasted_country_list, 2, 6, 1, 4)

        self.start_year_label = QLabel("Start Year:")
        layout.addWidget(self.start_year_label, 3, 0)
        self.start_year_spin = QSpinBox()
        self.start_year_spin.setRange(1900, 2100)
        layout.addWidget(self.start_year_spin, 3, 1)

        self.end_year_label = QLabel("End Year:")
        layout.addWidget(self.end_year_label, 3, 2)
        self.end_year_spin = QSpinBox()
        self.end_year_spin.setRange(1900, 2100)
        layout.addWidget(self.end_year_spin, 3, 3)

        self.test_button = QPushButton("ADF Test")
        self.test_button.clicked.connect(self.run_adf_test)
        layout.addWidget(self.test_button, 3, 4)

        self.plot_type_label = QLabel("Plot Type:")
        layout.addWidget(self.plot_type_label, 4, 0)
        self.plot_combo = QComboBox()
        self.plot_combo.addItems(["Historical", "Forecast", "Both"])
        layout.addWidget(self.plot_combo, 4, 1)

        self.chart_type_label = QLabel("Chart Type:")
        layout.addWidget(self.chart_type_label, 4, 2)
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Lines", "Stacked Bars"])
        layout.addWidget(self.chart_type_combo, 4, 3)

        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.plot_selected_data)
        layout.addWidget(self.plot_button, 4, 4)
        
        self.group_button = QPushButton("Group")
        self.group_button.clicked.connect(self.group_countries)
        layout.addWidget(self.group_button, 4, 5)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console, 5, 0, 1, 10)

        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.canvas, 6, 0, 1, 10)

        self.download_button = QPushButton("💾")
        self.download_button.setToolTip("Download plot as image")
        self.download_button.clicked.connect(self.download_plot)
        self.download_button.setFixedSize(30, 30)
        layout.addWidget(self.download_button, 6, 9, 1, 1)

        self.df = None
        self.adf_results = None
        self.filtered_data = None
        self.sarimax_results = None
        self.arimax_results = None
        self.arima_results = None
        self.forecast_results = {}
        self.sidePanelWindow = None
        self.forecast_until_year = 2100
        self.replace_negative_forecast = False
        
        self.active_lines = [] 

        self.save_dialog = SaveDialog(self)
        
    def show_save_dialog(self):
        """
        Show the save dialog to select the type of data to save.
        """
        self.save_dialog.show()
        
    def add_line(self, name, value, color, line_type, axis):
        """
        Add a line to the plot.
        """
        self.active_lines.append({
            'name': name,
            'value': value,
            'color': color,
            'type': line_type,
            'axis': axis,
            'active': True
        })
        self.update_sidepanel_lines()

    def closeEvent(self, event):
        """
        Handle the event of closing the side panel when closing the main window.

        Args:
            event (QCloseEvent): The close event.
        """
        if self.sidePanelWindow and self.sidePanelWindow.isVisible():
            self.sidePanelWindow.close()
        event.accept()

    def load_file(self):
        """
        Load a CSV file and update the UI with the loaded data.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load CSV File", self.dataset_dir, "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            try:
                self.df = pd.read_csv(file_name)
                self.update_combos()
                self.console.append(f"File {file_name} loaded successfully.")
            except Exception as e:
                self.console.append(f"Error loading file: {e}")

    def update_combos(self):
        """
        Update combo boxes and lists with the loaded data.
        """
        if self.df is not None:
            countries = self.df['Country'].unique().tolist()
            self.country_list.clear()
            self.forecasted_country_list.clear()

            for country in countries:
                country_item = QListWidgetItem(country)
                country_item.setFlags(country_item.flags() | Qt.ItemIsUserCheckable)
                country_item.setCheckState(Qt.Unchecked)
                self.country_list.addItem(country_item)

            variables = self.df.columns[2:].tolist()
            self.variable_combo.clear()
            self.variable_combo.addItems(variables)

            years = self.df['Date'].unique()
            self.start_year_spin.setRange(int(years.min()), int(years.max()))
            self.end_year_spin.setRange(int(years.min()), int(years.max()))
            self.start_year_spin.setValue(int(years.min()))
            self.end_year_spin.setValue(int(years.max()))

    def toggleSidePanel(self):
        """
        Toggle the visibility of the side panel(Hide the Side Panel).
        """
        if self.sidePanelWindow and self.sidePanelWindow.isVisible():
            self.sidePanelWindow.hide()
        else:
            if not self.sidePanelWindow:
                self.sidePanelWindow = SidePanelWindow(self)
            main_window_geometry = self.frameGeometry()
            side_panel_x = main_window_geometry.x() + main_window_geometry.width()
            side_panel_y = main_window_geometry.y()

            side_panel_height = self.geometry().height()

            self.sidePanelWindow.move(side_panel_x, side_panel_y)
            self.sidePanelWindow.resize(self.sidePanelWindow.width(), side_panel_height)
            self.sidePanelWindow.show()

    def group_countries(self):
        """
        Group selected countries into a single group.
        """
        selected_countries = self.get_selected_countries(self.country_list)
        if not selected_countries:
            self.console.append("Please select at least one country to group.")
            return
        self.group_panel = GroupPanelWindow(self)
        self.group_panel.show()

    def create_group(self, group_name):
        """
        Create a group with the specified name from selected countries.

        Args:
            group_name (str): The name of the group.
        """
        selected_countries = self.get_selected_countries(self.country_list)
        if not selected_countries:
            self.console.append("Please select at least one country to group.")
            return

        start_year = self.start_year_spin.value()
        end_year = self.end_year_spin.value()

        group_data = pd.DataFrame()
        for country in selected_countries:
            country_data = self.df[(self.df['Country'] == country) & (self.df['Date'] >= start_year) & (self.df['Date'] <= end_year)]
            if group_data.empty:
                group_data = country_data.copy()
            else:
                group_data = group_data.set_index('Date').add(country_data.set_index('Date'), fill_value=0).reset_index()

        group_data['Country'] = group_name

        self.df = pd.concat([self.df, group_data], ignore_index=True)

        self.update_combos()
        self.console.append(f"Group '{group_name}' created and added to the dataset.")
        self.country_search.setPlaceholderText("Search country...")

    def run_adf_test(self):
        """
        Run the Augmented Dickey-Fuller (ADF) test on the selected data.
        """
        if self.df is None:
            self.console.append("You must first load a CSV file.")
            return

        selected_countries = self.get_selected_countries(self.country_list)
        variable = self.variable_combo.currentText()
        start_year = self.start_year_spin.value()
        end_year = self.end_year_spin.value()

        if not selected_countries:
            self.console.append("Please select at least one country.")
            return

        self.adf_results = pd.DataFrame(columns=['Country', 'Variable', 'ADF Statistic', 'p-value', 'Num Lags', 'Num Observations', '1%', '5%', '10%', 'Differencing', 'p-value diff', 'Error'])

        for country in selected_countries:
            self.filtered_data = self.df[(self.df['Country'] == country) & (self.df['Date'] >= start_year) & (self.df['Date'] <= end_year)].copy()

            if self.filtered_data.empty:
                self.console.append(f"No data for country {country} and selected year range.")
                continue

            self.filtered_data.set_index('Date', inplace=True)

            adf_result = perform_adf_test_with_differencing(self.filtered_data[[variable]].dropna())
            if not adf_result.empty:
                adf_result['Country'] = country
                adf_result['Variable'] = variable
                self.adf_results = pd.concat([self.adf_results, adf_result], ignore_index=True)

        self.console.clear()
        self.console.append(self.format_adf_results(self.adf_results))

    def run_sarimax(self, p_range=None, d_range=None, q_range=None, seasonal_period=None):
        """
        Run the SARIMAX model optimization and forecasting.

        Args:
            p_range (range): Range of p values.
            d_range (range): Range of d values.
            q_range (range): Range of q values.
            seasonal_period (int): Seasonal period.
        """
        if self.adf_results is None or self.df is None:
            self.console.append("You must first run the ADF test.")
            return

        p_range = p_range if p_range is not None else range(0, 2)
        d_range = d_range if d_range is not None else range(0, 2)
        q_range = q_range if q_range is not None else range(0, 2)
        seasonal_period = seasonal_period if seasonal_period is not None else 11

        selected_countries = self.get_selected_countries(self.country_list)
        start_year = self.start_year_spin.value()
        end_year = self.end_year_spin.value()

        sarimax_results = optimize_sarimax_models(self.adf_results, self.df, selected_countries, p_range, d_range, q_range, seasonal_period, start_year, end_year)
        self.console.clear()
        self.console.append(self.format_sarimax_results(sarimax_results))

        forecast_results = forecast_future_sarimax(sarimax_results, self.df, start_year, self.forecast_until_year, self.replace_negative_forecast)
        self.forecast_results.update(forecast_results)

        self.apply_forecast_corrections()
        self.update_forecasted_countries_list()

    def run_arimax(self, p_range=None, d_range=None, q_range=None):
        """
        Run the ARIMAX model optimization and forecasting.

        Args:
            p_range (range): Range of p values.
            d_range (range): Range of d values.
            q_range (range): Range of q values.
        """
        if self.adf_results is None or self.df is None:
            self.console.append("You must first run the ADF test.")
            return

        p_range = p_range if p_range is not None else range(0, 2)
        d_range = d_range if d_range is not None else range(0, 2)
        q_range = q_range if q_range is not None else range(0, 2)

        selected_countries = self.get_selected_countries(self.country_list)
        start_year = self.start_year_spin.value()
        end_year = self.end_year_spin.value()

        for country in selected_countries:
            if self.adf_results[self.adf_results['Country'] == country].empty:
                self.console.append(f"No ADF results found for country {country}.")
                return

        arimax_results = optimize_arimax_models(self.adf_results, self.df, selected_countries, p_range, d_range, q_range, start_year, end_year)
        self.console.clear()
        self.console.append(self.format_arimax_results(arimax_results))

        forecast_results = forecast_future_arimax(arimax_results, self.df, start_year, self.forecast_until_year, self.replace_negative_forecast)
        self.forecast_results.update(forecast_results)

        self.apply_forecast_corrections()
        self.update_forecasted_countries_list()

    def run_arima(self, p_range=None, d_range=None, q_range=None):
        """
        Run the ARIMA model optimization and forecasting.

        Args:
            p_range (range): Range of p values.
            d_range (range): Range of d values.
            q_range (range): Range of q values.
        """
        if self.adf_results is None or self.df is None:
            self.console.append("You must first run the ADF test.")
            return

        p_range = p_range if p_range is not None else range(0, 2)
        d_range = d_range if d_range is not None else range(0, 2)
        q_range = q_range if q_range is not None else range(0, 2)

        selected_countries = self.get_selected_countries(self.country_list)
        start_year = self.start_year_spin.value()
        end_year = self.end_year_spin.value()

        for country in selected_countries:
            if self.adf_results[self.adf_results['Country'] == country].empty:
                self.console.append(f"No ADF results found for country {country}.")
                return

        arima_results = optimize_arima_models(self.adf_results, self.df, selected_countries, p_range, d_range, q_range, start_year, end_year)
        self.console.clear()
        self.console.append(self.format_arima_results(arima_results))

        forecast_results = forecast_future_arima(arima_results, self.df, start_year, self.forecast_until_year, self.replace_negative_forecast)
        self.forecast_results.update(forecast_results)

        self.apply_forecast_corrections()
        self.update_forecasted_countries_list()

    def apply_forecast_corrections(self):
        """
        Apply corrections to the forecasted data.
        """
        if self.sidePanelWindow is not None:
            selected_country = self.get_selected_countries(self.forecasted_country_list)  
            if not selected_country:
                self.console.append("Please select a country in the forecast country search list.")
                return

            target_year_text = self.sidePanelWindow.target_year_input.text()
            start_target_year_text = self.sidePanelWindow.start_target_year_input.text()  
            target_value_text = self.sidePanelWindow.target_value_input.text()
            continuous_correction = self.sidePanelWindow.continuous_correction_checkbox.isChecked()
            short_correction = self.sidePanelWindow.short_correction_checkbox.isChecked()
            start_correction = self.sidePanelWindow.start_correction_checkbox.isChecked()

            if target_year_text and target_value_text:
                target_year = int(target_year_text)
                target_value = float(target_value_text)
                start_target_year = int(start_target_year_text) if start_target_year_text else None  
                variable = self.variable_combo.currentText()
                self.apply_linear_correction(selected_country[0], target_year, start_target_year, target_value, variable, continuous_correction, short_correction, start_correction)

    def apply_linear_correction(self, country, target_year, start_target_year, target_value, variable, continuous, short, start):
        """
        Apply linear correction to the forecasted data.

        Args:
            country (str): The country for which to apply the correction.
            target_year (int): The target year for the correction.
            start_target_year (int): The start target year for the correction (optional).
            target_value (float): The target value for the correction.
            variable (str): The variable to correct.
            continuous (bool): Whether to apply continuous correction.
            short (bool): Whether to apply short correction.
            start (bool): Whether to apply start correction.
        """
        forecast_key = None
        for key, value in self.forecast_results.items():
            if country in key: 
                forecast_key = key
                break

        if not forecast_key:
            self.console.append(f"No forecast found for selected country: {country}")
            return

        forecast_data = self.forecast_results[forecast_key]
        forecast_values = forecast_data['forecast_values']
        forecast_years = forecast_values.index

        if target_year in forecast_years:
            start_year = start_target_year if start_target_year else forecast_years.min()
            if start:
                for year in forecast_years:
                    if start_year <= year <= target_year:
                        forecast_values.loc[year] = target_value
            else:
                current_value = forecast_values.loc[target_year]
                correction_factor = (target_value - current_value) / (target_year - start_year)

                for year in forecast_years:
                    if start_year <= year <= target_year:
                        forecast_values.loc[year] += correction_factor * (year - start_year)
                    elif year > target_year:
                        if continuous:
                            forecast_values.loc[year] += correction_factor * (year - start_year)
                        elif short:
                            forecast_values.loc[year] = target_value

            forecast_values[forecast_values < 0] = 0

    def update_forecasted_countries_list(self):
        """
        Update the list of forecasted countries.
        """
        self.forecasted_country_list.clear()
        forecasted_countries = list(self.forecast_results.keys())

        for forecast_key in forecasted_countries:
            forecasted_country_item = QListWidgetItem(forecast_key)
            forecasted_country_item.setFlags(forecasted_country_item.flags() | Qt.ItemIsUserCheckable)
            forecasted_country_item.setCheckState(Qt.Unchecked)
            self.forecasted_country_list.addItem(forecasted_country_item)

        self.forecasted_country_search.clear()

    def add_line(self, name, value, color, line_type):
        """
        Add a new line to the active lines list.

        Args:
            name (str): Name of the line.
            value (float): Value at which the line will be drawn.
            color (str): Color of the line.
            line_type (str): Type of the line (solid, dashed, dotted).
        """
        try:
            value = float(value)
            line = {'name': name, 'value': value, 'color': color, 'type': line_type, 'active': True}
            self.active_lines.append(line)
            self.console.append(f"Added line: {line}")
        except ValueError:
            self.console.append("Invalid value for the line.")

    def plot_selected_data(self):
        """
        Plot the selected data.
        """
        plot_type = self.plot_combo.currentText()
        chart_type = self.chart_type_combo.currentText()
        selected_forecasts = self.get_selected_countries(self.forecasted_country_list)
        selected_countries = self.get_selected_countries(self.country_list)
        variable = self.variable_combo.currentText()

        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)

        if plot_type == "Historical" and not selected_forecasts and self.df is not None:
            if chart_type == "Lines":
                plot_historical_data(self.df, selected_countries, variable, self.start_year_spin.value(), self.end_year_spin.value(), ax)
            elif chart_type == "Stacked Bars":
                plot_historical_data_bar(self.df, selected_countries, variable, self.start_year_spin.value(), self.end_year_spin.value(), ax)
            ax.set_xlim([self.start_year_spin.value(), self.end_year_spin.value()])
        else:
            if self.forecast_results is None:
                self.console.append("You must first apply a model.")
                return

            if not selected_forecasts:
                self.console.append("Please select at least one forecast to plot.")
                return

            show_confidence_interval = self.sidePanelWindow.show_confidence_interval_checkbox.isChecked()
            if show_confidence_interval and len(selected_forecasts) > 1:
                self.console.append("The 'Show Confidence Interval' option is only available for one country at a time.")
                return

            add_forecast_start_line = True
            if chart_type == "Lines":
                max_value = -float('inf')
                for forecast_key in selected_forecasts:
                    max_value = max(max_value, plot_data(self.df, self.forecast_results, forecast_key, variable, plot_type, ax, add_forecast_start_line, show_confidence_interval))
                    add_forecast_start_line = False
            elif chart_type == "Stacked Bars":
                max_value = plot_data_stacked_bar(self.df, self.forecast_results, selected_forecasts, variable, plot_type, ax)

            if plot_type == "Historical":
                start_year = self.start_year_spin.value()
                end_year = self.end_year_spin.value()
            elif plot_type == "Forecast":
                start_year = 2023
                end_year = self.forecast_until_year
            elif plot_type == "Both":
                start_year = self.start_year_spin.value()
                end_year = self.forecast_until_year

            ax.set_xlim([start_year, end_year])
            ax.set_ylim([0, max_value * 1.01])

        for line in self.active_lines:
            if line['active']:
                linestyle = '-' if line['type'] == 'solid' else '--' if line['type'] == 'dashed' else ':'
                if line['axis'] == 'x-axis':
                    ax.axvline(x=line['value'], color=line['color'], linestyle=linestyle, label=line['name'])
                else:
                    ax.axhline(y=line['value'], color=line['color'], linestyle=linestyle, label=line['name'])

        self.canvas.draw()

    def apply_plot_settings(self, x_range, y_range, title, legend_size, legend_position, xlabel, ylabel, xlabel_size, ylabel_size):
        """
        Apply plot settings to the current plot.

        Args:
            x_range (tuple): Range for the x-axis.
            y_range (tuple): Range for the y-axis.
            title (str): Title of the plot.
            legend_size (int): Font size for the legend.
            legend_position (str): Position for the legend.
            xlabel (str): Label for the x-axis.
            ylabel (str): Label for the y-axis.
            xlabel_size (int): Font size for the x-axis label.
            ylabel_size (int): Font size for the y-axis label.
        """
        if self.canvas.figure.axes:
            ax = self.canvas.figure.axes[0]
            if x_range and len(x_range) == 2:
                ax.set_xlim(x_range)
            if y_range and len(y_range) == 2:
                ax.set_ylim(y_range)
            if title:
                ax.set_title(title, fontsize=16, fontweight='bold')
            if legend_size:
                legend_position_mapping = {
                    "upperleft": "upper left",
                    "bottomleft": "lower left",
                    "upperright": "upper right",
                    "bottomright": "lower right"
                }
                legend_pos = legend_position_mapping.get(legend_position, "upper right")
                ax.legend(fontsize=legend_size, loc=legend_pos)
            if xlabel:
                ax.set_xlabel(xlabel, fontsize=xlabel_size if xlabel_size else 14)
            if ylabel:
                ax.set_ylabel(ylabel, fontsize=ylabel_size if ylabel_size else 14)
            if xlabel_size and not xlabel:
                ax.xaxis.label.set_size(xlabel_size)
            if ylabel_size and not ylabel:
                ax.yaxis.label.set_size(ylabel_size)
            self.canvas.draw()

    def save_forecast(self, save_type, save_path):
        """
        Save the selected type of data to a CSV file.

        Args:
            save_type (str): The type of data to save ("Historical", "Forecast", "Both").
            save_path (str): The path to save the CSV file.
        """
        selected_forecast_keys = self.get_selected_countries(self.forecasted_country_list)
        if not selected_forecast_keys:
            self.console.append("Please select at least one forecasted country to save.")
            return

        variable = self.variable_combo.currentText()
        save_data = pd.DataFrame()

        countries = [key.split(" ")[0] for key in selected_forecast_keys]
        for country in countries:
            if save_type in ["Historical", "Both"]:
                historical_data = self.df[(self.df['Country'] == country) & (self.df['Date'].notna())][['Country', 'Date', variable]]
                save_data = pd.concat([save_data, historical_data], ignore_index=True)

            if save_type in ["Forecast", "Both"]:
                forecast_key = next((key for key in selected_forecast_keys if country in key), None)
                if forecast_key:
                    forecast_values = self.forecast_results[forecast_key]['forecast_values']
                    forecast_years = forecast_values.index
                    forecast_df = pd.DataFrame({
                        'Country': country,
                        'Date': forecast_years,
                        variable: forecast_values.values
                    })
                    save_data = pd.concat([save_data, forecast_df], ignore_index=True)

        save_data.to_csv(save_path, index=False)
        self.console.append(f"Data saved to {save_path}")


    def download_plot(self):
        """
        Download the current plot as an image.
        """
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Plot Image", self.plot_dir, "PNG Files (*.png);;All Files (*)", options=options)
        if save_path:
            self.canvas.figure.savefig(save_path)
            self.canvas.figure.savefig(save_path, dpi=400)
            self.console.append(f"Plot saved to {save_path}")

    def filter_country_list(self):
        """
        Filter the list of countries based on the search input.
        """
        filter_text = self.country_search.text().lower()
        for index in range(self.country_list.count()):
            item = self.country_list.item(index)
            item.setHidden(filter_text not in item.text().lower())

    def filter_forecasted_country_list(self):
        """
        Filter the list of forecasted countries based on the search input.
        """
        filter_text = self.forecasted_country_search.text().lower()
        for index in range(self.forecasted_country_list.count()):
            item = self.forecasted_country_list.item(index)
            item.setHidden(filter_text not in item.text().lower())

    def format_adf_results(self, adf_results):
        """
        Format ADF test results as HTML.

        Args:
            adf_results (pd.DataFrame): The ADF test results.

        Returns:
            str: The formatted results in HTML.
        """
        if adf_results.empty:
            return "No results to display."
        return adf_results.to_html(index=False)

    def format_sarimax_results(self, sarimax_results):
        """
        Format SARIMAX results as HTML.

        Args:
            sarimax_results (dict): The SARIMAX results.

        Returns:
            str: The formatted results in HTML.
        """
        formatted_results = ""
        for country, result in sarimax_results.items():
            if 'model_object' in result:
                summary_html = result['model_summary'].as_html()
                formatted_results += f"<b>SARIMAX results for {country}:</b><br>{summary_html}<br>"
            else:
                formatted_results += f"<b>Failed to model {country}:</b> {result['error']}<br>"
        return formatted_results

    def format_arimax_results(self, arimax_results):
        """
        Format ARIMAX results as HTML.

        Args:
            arimax_results (dict): The ARIMAX results.

        Returns:
            str: The formatted results in HTML.
        """
        formatted_results = ""
        for country, result in arimax_results.items():
            if 'model_object' in result:
                summary_html = result['model_summary'].as_html()
                formatted_results += f"<b>ARIMAX results for {country}:</b><br>{summary_html}<br>"
            else:
                formatted_results += f"<b>Failed to model {country}:</b> {result['error']}<br>"
        return formatted_results

    def format_arima_results(self, arima_results):
        """
        Format ARIMA results as HTML.

        Args:
            arima_results (dict): The ARIMA results.

        Returns:
            str: The formatted results in HTML.
        """
        formatted_results = ""
        for country, result in arima_results.items():
            if 'model_object' in result:
                summary_html = result['model_summary'].as_html()
                formatted_results += f"<b>ARIMA results for {country}:</b><br>{summary_html}<br>"
            else:
                formatted_results += f"<b>Failed to model {country}:</b> {result['error']}<br>"
        return formatted_results

    def get_selected_countries(self, list_widget):
        """
        Get the list of selected countries from a QListWidget.

        Args:
            list_widget (QListWidget): The list widget containing the countries.

        Returns:
            list: The list of selected countries.
        """
        selected_countries = []
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            if item.checkState() == Qt.Checked:
                selected_countries.append(item.text())
        return selected_countries

    def clear_all(self):
        """
        Clear all selected forecasted models.
        """
        selected_forecasts = self.get_selected_countries(self.forecasted_country_list)
        if not selected_forecasts:
            self.console.append("No forecasted countries selected to delete.")
            return

        for forecast_key in selected_forecasts:
            if forecast_key in self.forecast_results:
                del self.forecast_results[forecast_key]

        self.update_forecasted_countries_list()
        self.console.append("Selected models successfully deleted.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
