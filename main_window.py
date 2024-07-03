import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QComboBox, QTextEdit, QFileDialog, QLabel, QSpinBox, QListWidget, QListWidgetItem, QLineEdit, QGridLayout, QMessageBox, QAction)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from adf_test import perform_adf_test
from sarimax import optimize_sarimax_models, forecast_future as forecast_future_sarimax
from arima import optimize_arima_models, forecast_future as forecast_future_arima
from plotting import plot_data, plot_data_stacked_bar, plot_historical_data, plot_historical_data_bar
from side_panel import SidePanelWindow
from group_panel import GroupPanelWindow
from save_panel import SavePanel
from about import AboutWindow

class MainWindow(QMainWindow):
    """
    Main window class for the forecasting application.

    This class initializes and sets up the main window for the forecasting application,
    managing user interactions and handling various functionalities such as loading data,
    running statistical tests, and plotting data.

    Attributes
    ----------
    df : pandas.DataFrame
        DataFrame to hold the dataset.
    adf_results : pandas.DataFrame
        DataFrame to hold the ADF test results.
    filtered_data : pandas.DataFrame
        DataFrame to hold the filtered data based on user selections.
    sarimax_results : dict
        Dictionary to hold SARIMAX model results.
    arima_results : dict
        Dictionary to hold ARIMA model results.
    forecast_results : dict
        Dictionary to hold forecast results.
    sidePanelWindow : SidePanelWindow
        Instance of the side panel window.
    forecast_until_year : int
        The year until which the forecast should be made.
    replace_negative_forecast : bool
        Flag to replace negative forecast values with zero.
    active_lines : list
        List of active lines for plotting.
    save_panel : SavePanel
        Instance of the save panel.
    """
    
    def __init__(self):
        """
        Initializes the MainWindow instance.

        This constructor initializes the main window, sets up the user interface,
        initializes necessary variables, and sets up required directories.
        """
        super().__init__()

        self.setup_ui()
        self.setup_directories()
        self.initialize_variables()

    def setup_ui(self):
        """
        Sets up the user interface elements and layout.

        This method configures the main window's title, size, and icon,
        and initializes various widgets including search bars, lists,
        combo boxes, spin boxes, buttons, text edit, and a matplotlib canvas.
        """
        self.setWindowTitle("Forecasting")
        self.setGeometry(100, 100, 1100, 900)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "Logo_NBackground.png")
        self.setWindowIcon(QIcon(icon_path))

        self.create_menu_bar()

        container = QWidget()
        self.setCentralWidget(container)
        layout = QGridLayout(container)

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

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console, 5, 0, 1, 10)

        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.canvas, 6, 0, 1, 10)

    def create_button(self, text, callback, layout, row, col, size=(30, 30)):
        """
        Creates a button with the specified parameters.

        Parameters
        ----------
        text : str
            The text to display on the button.
        callback : function
            The function to call when the button is clicked.
        layout : QGridLayout
            The layout to which the button should be added.
        row : int
            The row position in the layout.
        col : int
            The column position in the layout.
        size : tuple, optional
            The size of the button (default is (30, 30)).

        Returns
        -------
        QPushButton
            The created button.
        """
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setFixedSize(*size)
        layout.addWidget(button, row, col)
        return button
    
    def create_menu_bar(self):
        """
        Creates the menu bar for the main window.

        This method sets up the menu bar with 'File', 'Edit', 'Tools', 'Window', and 'Help' menus,
        and adds actions to these menus for functionalities such as loading, saving files, clearing console,
        running ADF tests, and showing the about window.
        """
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('File')
        edit_menu = menu_bar.addMenu('Edit')
        tools_menu = menu_bar.addMenu('Tools')       
        window_menu = menu_bar.addMenu('Window')
        help_menu = menu_bar.addMenu('Help')

        load_action = QAction('Open File...', self)
        load_action.triggered.connect(self.load_file)
        save_action = QAction('Save File...', self)
        save_action.triggered.connect(self.show_save_panel)
        save_plot_action = QAction('Save Plot...', self)
        save_plot_action.triggered.connect(self.download_plot)
        file_menu.addAction(load_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_plot_action)

        group_action = QAction('Group Country`s', self)
        group_action.triggered.connect(self.group_countries)
        clear_console_action = QAction('Clear Console', self)
        clear_console_action.triggered.connect(self.clear_console)
        clear_forecasts_action = QAction('Clear Forecasts List', self)
        clear_forecasts_action.triggered.connect(self.clear_all)
        edit_menu.addAction(group_action)
        edit_menu.addAction(clear_console_action)
        edit_menu.addAction(clear_forecasts_action)

        toggle_side_panel_action = QAction('Open Forecast Panel', self)
        toggle_side_panel_action.triggered.connect(self.toggleSidePanel)
        window_menu.addAction(toggle_side_panel_action)

        adf_test_action = QAction('ADF Test', self)
        adf_test_action.triggered.connect(self.run_adf_test)
        tools_menu.addAction(adf_test_action)

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def show_about(self):
        """
        Displays the about window.

        This method creates an instance of the AboutWindow class and shows it.
        """
        self.about_window = AboutWindow()
        self.about_window.show()

    def setup_directories(self):
        """
        Sets up necessary directories for data and plots.

        This method creates directories for storing datasets, extracted datasets, and plots
        if they do not already exist.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.dataset_dir = os.path.join(script_dir, "dataset")
        self.extracted_dataset_dir = os.path.join(script_dir, "extracted_dataset")
        self.plot_dir = os.path.join(script_dir, "plot")

        os.makedirs(self.dataset_dir, exist_ok=True)
        os.makedirs(self.extracted_dataset_dir, exist_ok=True)
        os.makedirs(self.plot_dir, exist_ok=True)

    def initialize_variables(self):
        """
        Initializes variables used in the main window.

        This method initializes various instance variables such as dataframes, result dictionaries,
        and UI-related variables.
        """
        self.df = None
        self.adf_results = None
        self.filtered_data = None
        self.sarimax_results = None
        self.arima_results = None
        self.forecast_results = {}
        self.sidePanelWindow = None
        self.forecast_until_year = 2100
        self.replace_negative_forecast = False
        self.active_lines = []  
        self.save_panel = SavePanel(self)
    
    def show_save_panel(self):
        """
        Displays the save panel.

        This method shows the save panel for saving data.
        """
        self.save_panel.show()
        
    def add_line(self, name, value, color, line_type, axis):
        """
        Adds a line to the plot.

        Parameters
        ----------
        name : str
            The name of the line.
        value : float
            The value at which the line should be drawn.
        color : str
            The color of the line.
        line_type : str
            The type of the line (solid, dashed, etc.).
        axis : str
            The axis on which the line should be drawn (x-axis or y-axis).

        This method adds a new line to the active lines list and updates the side panel.
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
        Handles the close event of the main window.

        Parameters
        ----------
        event : QCloseEvent
            The close event.

        This method closes the side panel window if it is open and accepts the event.
        """
        if self.sidePanelWindow and self.sidePanelWindow.isVisible():
            self.sidePanelWindow.close()
        event.accept()

    def load_file(self):
        """
        Opens a file dialog to load a CSV file.

        This method opens a QFileDialog to allow the user to select and load a CSV file.
        If a file is selected, it processes the loaded file.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load CSV File", self.dataset_dir, "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            self.process_loaded_file(file_name)

    def process_loaded_file(self, file_name):
        """
        Processes the loaded CSV file.

        Parameters
        ----------
        file_name : str
            The path of the file to be processed.

        This method reads the CSV file into a DataFrame, converts it if necessary,
        and merges or replaces the existing DataFrame.
        """
        try:
            new_df = pd.read_csv(file_name)
            self.console.append(f"File {file_name} loaded successfully.")

            if 'Country' in new_df.columns:
                new_format_df = new_df
            else:
                new_format_df = self.convert_new_format_to_original(new_df)

            self.merge_or_replace_dataframe(new_format_df)
            self.update_combos()
        except Exception as e:
            self.console.append(f"Error loading file: {e}")

    def convert_new_format_to_original(self, new_df):
        """
        Converts new format DataFrame to original format.

        Parameters
        ----------
        new_df : pandas.DataFrame
            The new format DataFrame.

        Returns
        -------
        pandas.DataFrame
            The converted DataFrame in the original format.

        This method converts a DataFrame from the new format to the original format expected by the application.
        """
        melted_df = new_df.melt(id_vars=['Date', 'Variable'], var_name='Country', value_name='Value')
        variable_name = melted_df['Variable'].iloc[0]
        melted_df = melted_df.rename(columns={'Value': variable_name}).drop(columns=['Variable'])
        return melted_df

    def merge_or_replace_dataframe(self, new_format_df):
        """
        Merges or replaces the existing DataFrame with a new one.

        Parameters
        ----------
        new_format_df : pandas.DataFrame
            The new format DataFrame to be merged or replaced.

        This method merges the new DataFrame with the existing one if the user chooses to merge,
        or replaces the existing DataFrame with the new one.
        """
        if self.df is not None:
            reply = QMessageBox.question(self, 'Merge Datasets', 'Do you want to merge the new dataset with the existing one?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.df = pd.concat([self.df, new_format_df], ignore_index=True)
            else:
                self.df = new_format_df
        else:
            self.df = new_format_df

    def update_combos(self):
        """
        Updates combo boxes with data from the DataFrame.

        This method populates the country list, variable combo box,
        and sets the range for the year spin boxes based on the DataFrame.
        """
        if self.df is not None:
            self.populate_country_list(self.df['Country'].unique().tolist())
            self.populate_variable_combo([col for col in self.df.columns if col not in ['Country', 'Date']])
            self.set_year_range(self.df['Date'].unique())

    def populate_country_list(self, countries):
        """
        Populates the country list widget.

        Parameters
        ----------
        countries : list of str
            The list of country names to populate.

        This method clears the existing items in the country list widget
        and adds new items for each country in the provided list.
        """
        self.country_list.clear()
        self.forecasted_country_list.clear()

        for country in countries:
            country_item = QListWidgetItem(country)
            country_item.setFlags(country_item.flags() | Qt.ItemIsUserCheckable)
            country_item.setCheckState(Qt.Unchecked)
            self.country_list.addItem(country_item)

    def populate_variable_combo(self, variables):
        """
        Populates the variable combo box.

        Parameters
        ----------
        variables : list of str
            The list of variable names to populate.

        This method clears the existing items in the variable combo box
        and adds new items for each variable in the provided list.
        """
        self.variable_combo.clear()
        self.variable_combo.addItems(variables)

    def set_year_range(self, years):
        """
        Sets the range of the year spin boxes.

        Parameters
        ----------
        years : array-like
            The array of years to determine the range.

        This method sets the minimum and maximum values for the start and end year spin boxes
        based on the provided array of years.
        """
        self.start_year_spin.setRange(int(years.min()), int(years.max()))
        self.end_year_spin.setRange(int(years.min()), int(years.max()))
        self.start_year_spin.setValue(int(years.min()))
        self.end_year_spin.setValue(int(years.max()))

    def toggleSidePanel(self):
        """
        Toggles the side panel visibility.

        This method shows or hides the side panel window based on its current visibility state.
        """
        if (self.sidePanelWindow and self.sidePanelWindow.isVisible()):
            self.sidePanelWindow.hide()
        else:
            if not self.sidePanelWindow:
                self.sidePanelWindow = SidePanelWindow(self)
            self.position_and_show_side_panel()

    def position_and_show_side_panel(self):
        """
        Positions and shows the side panel window.

        This method positions the side panel window next to the main window
        and sets its height to match the main window's height.
        """
        main_window_geometry = self.frameGeometry()
        side_panel_x = main_window_geometry.x() + main_window_geometry.width()
        side_panel_y = main_window_geometry.y()
        side_panel_height = self.geometry().height()

        self.sidePanelWindow.move(side_panel_x, side_panel_y)
        self.sidePanelWindow.resize(self.sidePanelWindow.width(), side_panel_height)
        self.sidePanelWindow.show()

    def group_countries(self):
        """
        Opens the group panel window to group selected countries.

        This method retrieves the selected countries from the country list,
        and if at least one country is selected, it opens the GroupPanelWindow.
        """
        selected_countries = self.get_selected_countries(self.country_list)
        if not selected_countries:
            self.console.append("Please select at least one country to group.")
            return
        self.group_panel = GroupPanelWindow(self)
        self.group_panel.show()

    def create_group(self, group_name):
        """
        Creates a group of selected countries.

        Parameters
        ----------
        group_name : str
            The name of the new group.

        This method aggregates data for the selected countries over the specified year range,
        creates a new group with the aggregated data, and updates the combo boxes.
        """
        selected_countries = self.get_selected_countries(self.country_list)
        if not selected_countries:
            self.console.append("Please select at least one country to group.")
            return

        start_year = self.start_year_spin.value()
        end_year = self.end_year_spin.value()
        group_data = self.aggregate_group_data(selected_countries, start_year, end_year, group_name)

        self.df = pd.concat([self.df, group_data], ignore_index=True)
        self.update_combos()
        self.console.append(f"Group '{group_name}' created and added to the dataset.")
        self.country_search.setPlaceholderText("Search country...")

    def aggregate_group_data(self, selected_countries, start_year, end_year, group_name):
        """
        Aggregates data for a group of countries.

        Parameters
        ----------
        selected_countries : list of str
            The list of selected countries.
        start_year : int
            The start year for the aggregation.
        end_year : int
            The end year for the aggregation.
        group_name : str
            The name of the group.

        Returns
        -------
        pandas.DataFrame
            The aggregated data for the group.

        This method aggregates data for the selected countries over the specified year range
        and creates a new DataFrame with the aggregated data.
        """
        group_data = pd.DataFrame()
        for country in selected_countries:
            country_data = self.df[(self.df['Country'] == country) & (self.df['Date'] >= start_year) & (self.df['Date'] <= end_year)]
            if group_data.empty:
                group_data = country_data.copy()
                group_data.set_index('Date', inplace=True)
            else:
                country_data.set_index('Date', inplace=True)
                numeric_cols = country_data.select_dtypes(include=['number']).columns
                group_data[numeric_cols] = group_data[numeric_cols].add(country_data[numeric_cols], fill_value=0)

        group_data.reset_index(inplace=True)
        group_data['Country'] = group_name
        return group_data

    def run_adf_test(self):
        """
        Runs the Augmented Dickey-Fuller test on the selected data.

        This method performs the ADF test on the selected data for the specified countries,
        variable, and year range, and appends the results to the console.
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

        self.adf_results = pd.DataFrame(columns=['Country', 'Variable', 'ADF Statistic', 'p-value', 'Num Lags', 'Num Observations', '1%', '5%', '10%', 'Stationary', 'Error'])

        for country in selected_countries:
            self.filtered_data = self.df[(self.df['Country'] == country) & (self.df['Date'] >= start_year) & (self.df['Date'] <= end_year)].copy()
            if self.filtered_data.empty:
                self.console.append(f"No data for country {country} and selected year range.")
                continue

            self.filtered_data.set_index('Date', inplace=True)
            adf_result = perform_adf_test(self.filtered_data[[variable]].dropna())
            if not adf_result.empty:
                adf_result['Country'] = country
                adf_result['Variable'] = variable
                self.adf_results = pd.concat([self.adf_results, adf_result], ignore_index=True) if not self.adf_results.empty else adf_result

        self.console.append("<hr style='border: 1px solid black;'>")
        self.console.append(self.format_adf_results(self.adf_results))

    def run_sarimax(self, p_range=None, d_range=None, q_range=None, seasonal_period=None, enable_seasonality=True):
        """
        Runs the SARIMAX model optimization.

        Parameters
        ----------
        p_range : range, optional
            Range of values for the p parameter (default is range(0, 2)).
        d_range : range, optional
            Range of values for the d parameter (default is range(0, 2)).
        q_range : range, optional
            Range of values for the q parameter (default is range(0, 2)).
        seasonal_period : int, optional
            Seasonal period for the SARIMAX model (default is 11).
        enable_seasonality : bool, optional
            Flag to enable or disable seasonality (default is True).

        This method optimizes SARIMAX models for the selected countries,
        plots the results, and updates the forecast results.
        """
        p_range = p_range if p_range is not None else range(0, 2)
        d_range = d_range if d_range is not None else range(0, 2)
        q_range = q_range if q_range is not None else range(0, 2)
        seasonal_period = seasonal_period if seasonal_period is not None else 11

        selected_countries = self.get_selected_countries(self.country_list)
        start_year = self.start_year_spin.value()
        end_year = self.end_year_spin.value()

        sarimax_results = optimize_sarimax_models(self.df, selected_countries, p_range, d_range, q_range, seasonal_period, start_year, end_year, enable_seasonality)
        self.console.append("<hr style='border: 1px solid black;'>")
        self.console.append(self.format_sarimax_results(sarimax_results))

        forecast_results = forecast_future_sarimax(sarimax_results, self.df, start_year, self.forecast_until_year, self.replace_negative_forecast)
        self.forecast_results.update(forecast_results)

        self.apply_forecast_corrections()
        self.update_forecasted_countries_list()

    def run_arima(self, p_range=None, d_range=None, q_range=None):
        """
        Runs the ARIMA model optimization.

        Parameters
        ----------
        p_range : range, optional
            Range of values for the p parameter (default is range(0, 2)).
        d_range : range, optional
            Range of values for the d parameter (default is range(0, 2)).
        q_range : range, optional
            Range of values for the q parameter (default is range(0, 2)).

        This method optimizes ARIMA models for the selected countries,
        plots the results, and updates the forecast results.
        """
        p_range = p_range if p_range is not None else range(0, 2)
        d_range = d_range if d_range is not None else range(0, 2)
        q_range = q_range if q_range is not None else range(0, 2)

        selected_countries = self.get_selected_countries(self.country_list)
        start_year = self.start_year_spin.value()
        end_year = self.end_year_spin.value()

        arima_results = optimize_arima_models(self.df, selected_countries, p_range, d_range, q_range, start_year, end_year)
        self.console.append("<hr style='border: 1px solid black;'>")
        self.console.append(self.format_arima_results(arima_results))

        forecast_results = forecast_future_arima(arima_results, self.df, start_year, self.forecast_until_year, self.replace_negative_forecast)
        self.forecast_results.update(forecast_results)

        self.apply_forecast_corrections()
        self.update_forecasted_countries_list()

    def apply_forecast_corrections(self):
        """
        Applies corrections to the forecast.

        This method checks if a forecast country is selected and applies the corrections
        specified in the side panel for the selected country.
        """
        if self.sidePanelWindow:
            selected_country = self.get_selected_countries(self.forecasted_country_list)
            if not selected_country:
                self.console.append("Please select a country in the forecast country search list.")
                return

            self.correct_forecast(selected_country[0])

    def correct_forecast(self, country):
        """
        Corrects the forecast for a specific country.

        Parameters
        ----------
        country : str
            The name of the country for which the forecast should be corrected.

        This method retrieves correction parameters from the side panel
        and applies a linear correction to the forecast data.
        """
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
            self.apply_linear_correction(country, target_year, start_target_year, target_value, variable, continuous_correction, short_correction, start_correction)

    def apply_linear_correction(self, country, target_year, start_target_year, target_value, variable, continuous, short, start):
        """
        Applies a linear correction to the forecast data.

        Parameters
        ----------
        country : str
            The name of the country for which the correction should be applied.
        target_year : int
            The target year for the correction.
        start_target_year : int, optional
            The start year for the correction.
        target_value : float
            The target value for the correction.
        variable : str
            The variable for which the correction should be applied.
        continuous : bool
            Flag to apply continuous correction.
        short : bool
            Flag to apply short correction.
        start : bool
            Flag to apply start correction.

        This method adjusts the forecast data linearly to match the target value by the target year,
        with optional parameters for continuous and short corrections.
        """
        forecast_key = self.get_forecast_key(country)
        if not forecast_key:
            self.console.append(f"No forecast found for selected country: {country}")
            return

        forecast_data = self.forecast_results[forecast_key]
        forecast_values = forecast_data['forecast_values']
        forecast_years = forecast_values.index

        if target_year in forecast_years:
            start_year = start_target_year if start_target_year else forecast_years.min()
            current_value = forecast_values.loc[start_year]
            correction_factor = (target_value - current_value) / (target_year - start_year)

            if start:
                for year in forecast_years:
                    if start_year <= year <= target_year:
                        forecast_values.loc[year] = target_value
            else:
                for year in forecast_years:
                    if start_year <= year <= target_year:
                        forecast_values.loc[year] = current_value + correction_factor * (year - start_year)
                    elif year > target_year:
                        if continuous:
                            forecast_values.loc[year] = forecast_values.loc[target_year] + correction_factor * (year - target_year)
                        elif short:
                            forecast_values.loc[year] = target_value

            forecast_values[forecast_values < 0] = 0

    def get_forecast_key(self, country):
        """
        Gets the forecast key for a specific country.

        Parameters
        ----------
        country : str
            The name of the country.

        Returns
        -------
        str or None
            The forecast key if found, otherwise None.

        This method searches the forecast results for the key corresponding to the given country.
        """
        for key, value in self.forecast_results.items():
            if country in key:
                return key
        return None

    def update_forecasted_countries_list(self):
        """
        Updates the list of forecasted countries.

        This method clears the existing items in the forecasted country list
        and adds new items for each key in the forecast results.
        """
        self.forecasted_country_list.clear()
        forecasted_countries = list(self.forecast_results.keys())

        for forecast_key in forecasted_countries:
            forecasted_country_item = QListWidgetItem(forecast_key)
            forecasted_country_item.setFlags(forecasted_country_item.flags() | Qt.ItemIsUserCheckable)
            forecasted_country_item.setCheckState(Qt.Unchecked)
            self.forecasted_country_list.addItem(forecasted_country_item)

        self.forecasted_country_search.clear()
        
    def plot_selected_data(self):
        """
        Plots the selected data.

        This method retrieves the selected plot type, chart type, forecasts, and countries,
        and plots the data on the matplotlib canvas.
        """
        plot_type = self.plot_combo.currentText()
        chart_type = self.chart_type_combo.currentText()
        selected_forecasts = self.get_selected_countries(self.forecasted_country_list)
        selected_countries = self.get_selected_countries(self.country_list)
        variable = self.variable_combo.currentText()

        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)

        if plot_type == "Historical" and not selected_forecasts and not self.df.empty:
            self.plot_historical_data(chart_type, selected_countries, variable, ax)
        else:
            self.plot_forecast_data(plot_type, chart_type, selected_forecasts, variable, ax)

        self.canvas.draw()

    def plot_historical_data(self, chart_type, selected_countries, variable, ax):
        """
        Plots historical data.

        Parameters
        ----------
        chart_type : str
            The type of chart to plot (Lines or Stacked Bars).
        selected_countries : list of str
            The list of selected countries.
        variable : str
            The variable to plot.
        ax : matplotlib.axes.Axes
            The axes object to plot on.

        This method plots historical data for the selected countries and variable
        using the specified chart type.
        """
        if chart_type == "Lines":
            plot_historical_data(self.df, selected_countries, variable, self.start_year_spin.value(), self.end_year_spin.value(), ax)
        elif chart_type == "Stacked Bars":
            plot_historical_data_bar(self.df, selected_countries, variable, self.start_year_spin.value(), self.end_year_spin.value(), ax)
        ax.set_xlim([self.start_year_spin.value(), self.end_year_spin.value()])

    def plot_forecast_data(self, plot_type, chart_type, selected_forecasts, variable, ax):
        """
        Plots forecast data.

        Parameters
        ----------
        plot_type : str
            The type of plot (Historical, Forecast, or Both).
        chart_type : str
            The type of chart to plot (Lines or Stacked Bars).
        selected_forecasts : list of str
            The list of selected forecast keys.
        variable : str
            The variable to plot.
        ax : matplotlib.axes.Axes
            The axes object to plot on.

        This method plots forecast data for the selected forecast keys and variable
        using the specified plot type and chart type.
        """
        if not self.forecast_results:
            self.console.append("You must first apply a model.")
            return

        if not selected_forecasts:
            self.console.append("Please select at least one forecast to plot.")
            return

        show_confidence_interval = self.sidePanelWindow.show_confidence_interval_checkbox.isChecked()
        if show_confidence_interval and len(selected_forecasts) > 1:
            self.console.append("The 'Show Confidence Interval' option is only available for one country at a time.")
            return

        max_value = -float('inf')
        if chart_type == "Lines":
            max_value = plot_data(self.df, self.forecast_results, selected_forecasts, variable, plot_type, ax)
        elif chart_type == "Stacked Bars":
            max_value = plot_data_stacked_bar(self.df, self.forecast_results, selected_forecasts, variable, plot_type, ax)

        self.set_plot_limits(ax, plot_type, max_value)

    def set_plot_limits(self, ax, plot_type, max_value):
        """
        Sets the plot limits.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes object to set limits on.
        plot_type : str
            The type of plot (Historical, Forecast, or Both).
        max_value : float
            The maximum value to set for the y-axis limit.

        This method sets the x-axis and y-axis limits for the plot
        based on the plot type and maximum value.
        """
        if plot_type == "Historical":
            start_year = self.start_year_spin.value()
            end_year = self.end_year_spin.value()
        elif plot_type == "Forecast":
            start_year = self.end_year_spin.value()
            end_year = self.forecast_until_year
        elif plot_type == "Both":
            start_year = self.start_year_spin.value()
            end_year = self.forecast_until_year

        ax.set_xlim([start_year, end_year])
        ax.set_ylim([0, max_value * 1.01])

    def save_forecast(self, save_type, format_type, save_path):
        """
        Saves the forecast data to a file.

        Parameters
        ----------
        save_type : str
            The type of data to save (Historical, Forecast, or Both).
        format_type : str
            The format to save the data in (Original or New).
        save_path : str
            The path to save the file.

        This method aggregates the data to be saved based on the specified type and format,
        and saves it to the specified file path.
        """
        selected_forecast_keys = self.get_selected_countries(self.forecasted_country_list)
        if not selected_forecast_keys:
            self.console.append("Please select at least one forecasted country to save.")
            return

        variable = self.variable_combo.currentText()
        save_data = self.aggregate_save_data(selected_forecast_keys, variable, save_type)

        if format_type == "Format 2 (New)":
            save_data = save_data.pivot(index='Date', columns='Country', values=variable).reset_index()
            save_data.insert(1, 'Variable', variable)

        save_data.to_csv(save_path, index=False)
        self.console.append(f"Data saved to {save_path}")

    def aggregate_save_data(self, selected_forecast_keys, variable, save_type):
        """
        Aggregates data to be saved.

        Parameters
        ----------
        selected_forecast_keys : list of str
            The list of selected forecast keys.
        variable : str
            The variable to save.
        save_type : str
            The type of data to save (Historical, Forecast, or Both).

        Returns
        -------
        pandas.DataFrame
            The aggregated data to be saved.

        This method aggregates historical and/or forecast data for the selected forecast keys
        and variable based on the specified save type.
        """
        save_data = pd.DataFrame()

        for forecast_key in selected_forecast_keys:
            country = forecast_key.split(' (')[0]
            if save_type in ["Historical", "Both"]:
                historical_data = self.df[(self.df['Country'] == country) & (self.df['Date'].notna())][['Country', 'Date', variable]]
                save_data = pd.concat([save_data, historical_data], ignore_index=True)

            if save_type in ["Forecast", "Both"]:
                forecast_values = self.forecast_results[forecast_key]['forecast_values']
                forecast_years = forecast_values.index
                forecast_df = pd.DataFrame({
                    'Country': country,
                    'Date': forecast_years,
                    variable: forecast_values.values
                })
                save_data = pd.concat([save_data, forecast_df], ignore_index=True)

        return save_data

    def download_plot(self):
        """
        Downloads the plot as an image.

        This method opens a QFileDialog to allow the user to specify a file path
        to save the current plot as an image file.
        """
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Plot Image", self.plot_dir, "PNG Files (*.png);;All Files (*)", options=options)
        if save_path:
            self.canvas.figure.savefig(save_path, dpi=400)
            self.console.append(f"Plot saved to {save_path}")

    def filter_country_list(self):
        """
        Filters the country list based on the search input.

        This method filters the items in the country list widget
        based on the text entered in the country search line edit.
        """
        self.filter_list(self.country_search.text().lower(), self.country_list)

    def filter_forecasted_country_list(self):
        """
        Filters the forecasted country list based on the search input.

        This method filters the items in the forecasted country list widget
        based on the text entered in the forecasted country search line edit.
        """
        self.filter_list(self.forecasted_country_search.text().lower(), self.forecasted_country_list)

    def filter_list(self, filter_text, list_widget):
        """
        Filters a list widget based on the filter text.

        Parameters
        ----------
        filter_text : str
            The text to filter the list items.
        list_widget : QListWidget
            The list widget to be filtered.

        This method hides or shows items in the list widget
        based on whether their text contains the filter text.
        """
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            item.setHidden(filter_text not in item.text().lower())

    def format_adf_results(self, adf_results):
        """
        Formats the ADF test results.

        Parameters
        ----------
        adf_results : pandas.DataFrame
            The ADF test results DataFrame.

        Returns
        -------
        str
            The formatted ADF test results in HTML.

        This method formats the ADF test results DataFrame as an HTML table.
        """
        if adf_results.empty:
            return "No results to display."
        return adf_results.to_html(index=False)

    def format_sarimax_results(self, sarimax_results):
        """
        Formats the SARIMAX model results.

        Parameters
        ----------
        sarimax_results : dict
            The SARIMAX model results.

        Returns
        -------
        str
            The formatted SARIMAX model results in HTML.

        This method formats the SARIMAX model results as an HTML summary.
        """
        return self.format_model_results(sarimax_results, "SARIMAX")

    def format_arima_results(self, arima_results):
        """
        Formats the ARIMA model results.

        Parameters
        ----------
        arima_results : dict
            The ARIMA model results.

        Returns
        -------
        str
            The formatted ARIMA model results in HTML.

        This method formats the ARIMA model results as an HTML summary.
        """
        return self.format_model_results(arima_results, "ARIMA")

    def format_model_results(self, results, model_name):
        """
        Formats the model results.

        Parameters
        ----------
        results : dict
            The model results.
        model_name : str
            The name of the model (SARIMAX or ARIMA).

        Returns
        -------
        str
            The formatted model results in HTML.

        This method formats the model results as an HTML summary,
        including the model summary and any errors encountered during modeling.
        """
        formatted_results = ""
        for country, result in results.items():
            if 'model_object' in result:
                summary_html = result['model_summary'].as_html()
                formatted_results += f"<b>{model_name} results for {country}:</b><br>{summary_html}<br>"
            else:
                formatted_results += f"<b>Failed to model {country}:</b> {result['error']}<br>"
        return formatted_results

    def get_selected_countries(self, list_widget):
        """
        Gets the list of selected countries.

        Parameters
        ----------
        list_widget : QListWidget
            The list widget containing country items.

        Returns
        -------
        list of str
            The list of selected countries.

        This method retrieves the names of countries that are checked
        in the specified list widget.
        """
        return [list_widget.item(index).text() for index in range(list_widget.count()) if list_widget.item(index).checkState() == Qt.Checked]

    def clear_all(self):
        """
        Clears all forecast results.

        This method deletes the selected forecast results from the forecast results dictionary
        and updates the forecasted country list.
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

    def clear_console(self):
        """
        Clears the console output.

        This method clears all text from the console text edit.
        """
        self.console.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
