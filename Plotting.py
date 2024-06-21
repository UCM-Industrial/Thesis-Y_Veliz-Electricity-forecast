import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_historical_data(df, selected_countries, variable, start_year, end_year, ax):
    """
    Plot historical data for the selected countries.

    Args:
        df (pd.DataFrame): Data frame containing the data.
        selected_countries (list): List of selected countries.
        variable (str): Variable to plot.
        start_year (int): Start year for the plot.
        end_year (int): End year for the plot.
        ax (matplotlib.axes.Axes): Matplotlib axis to plot on.

    Returns:
        float: Maximum value in the plotted data.
    """
    max_value = -float('inf')
    for country in selected_countries:
        country_data = df[(df['Country'] == country) & (df['Date'] >= start_year) & (df['Date'] <= end_year)]
        if not country_data.empty:
            max_value = max(max_value, country_data[variable].max())
            ax.plot(country_data['Date'], country_data[variable], label=country)
    ax.set_xlim([start_year, end_year])
    ax.set_ylim([0, max_value * 1.01])
    ax.legend()
    ax.set_title(f"{variable} Production (Historical)", fontsize=16, fontweight='bold')
    ax.set_ylabel('Production', fontsize=14)
    ax.set_xlabel('Year', fontsize=14)
    ax.grid(True, linestyle='--', which='both', color='grey', alpha=0.5)
    return max_value

def plot_historical_data_bar(df, selected_countries, variable, start_year, end_year, ax):
    """
    Plot historical data for the selected countries using bar charts.

    Args:
        df (pd.DataFrame): Data frame containing the data.
        selected_countries (list): List of selected countries.
        variable (str): Variable to plot.
        start_year (int): Start year for the plot.
        end_year (int): End year for the plot.
        ax (matplotlib.axes.Axes): Matplotlib axis to plot on.

    Returns:
        float: Maximum value in the plotted data.
    """
    combined_data = pd.DataFrame()

    for country in selected_countries:
        country_data = df[(df['Country'] == country) & (df['Date'] >= start_year) & (df['Date'] <= end_year)]
        if not country_data.empty:
            combined_data[country] = country_data.set_index('Date')[variable]

    combined_data = combined_data.fillna(0)
    bottom = pd.Series([0] * len(combined_data.index), index=combined_data.index)
    colors = plt.cm.tab20(np.linspace(0, 1, len(selected_countries)))
    max_value = combined_data.sum(axis=1).max()

    for i, country in enumerate(selected_countries):
        ax.bar(combined_data.index, combined_data[country], bottom=bottom, color=colors[i], label=country)
        bottom += combined_data[country]

    ax.set_xlim([start_year, end_year])
    ax.set_ylim([0, max_value * 1.01])
    ax.legend()
    ax.set_title(f"{variable} Production (Historical)", fontsize=16, fontweight='bold')
    ax.set_ylabel('Production', fontsize=14)
    ax.set_xlabel('Year', fontsize=14)
    ax.grid(True, linestyle='--', which='both', color='grey', alpha=0.5)
    return max_value

def plot_data(df, forecast_results, forecast_key, variable, plot_type, ax, add_forecast_start_line, show_confidence_interval):
    """
    Plot data and forecasts on a matplotlib axis.

    Args:
        df (pd.DataFrame): Data frame containing the data.
        forecast_results (dict): Forecast results.
        forecast_key (str): Key for the forecast result.
        variable (str): Variable to plot.
        plot_type (str): Type of plot ("Historical", "Forecast", "Both").
        ax (matplotlib.axes.Axes): Matplotlib axis to plot on.
        add_forecast_start_line (bool): Whether to add a line indicating the start of the forecast.
        show_confidence_interval (bool): Whether to show confidence intervals.

    Returns:
        float: Maximum value in the plotted data.
    """
    forecast = forecast_results[forecast_key]
    country = forecast['country']
    historical_data = df[df['Country'] == country][['Date', variable]].set_index('Date')

    min_year = int(historical_data.index.min())
    max_year = int(historical_data.index.max())
    forecast_years = range(2023, forecast['forecast_until_year'] + 1)

    combined_data = pd.DataFrame(index=range(min_year, forecast['forecast_until_year'] + 1))
    combined_data[variable] = historical_data[variable]

    if forecast_key in forecast_results:
        forecast_values = forecast_results[forecast_key]['forecast_values']
        forecast_ci = forecast_results[forecast_key]['forecast_ci']
        forecast_index = forecast_values.index

        combined_data.loc[forecast_index, variable] = forecast_values

    historical_part = combined_data.loc[:max_year, variable].dropna()
    forecast_part = combined_data.loc[forecast_years, variable].dropna()

    max_value = max(historical_part.max(), forecast_part.max())

    if plot_type == "Historical":
        ax.plot(historical_part.index, historical_part, label=f'Historical - {country}')
    elif plot_type == "Forecast":
        ax.plot(forecast_part.index, forecast_part, label=f'Forecast - {country}', linestyle='--')
        if show_confidence_interval:
            ax.fill_between(forecast_ci.index, forecast_ci['mean_ci_lower'], forecast_ci['mean_ci_upper'], color='gray', alpha=0.2)
    elif plot_type == "Both":
        combined_part = pd.concat([historical_part, forecast_part])
        ax.plot(combined_part.index, combined_part, label=country)
        if show_confidence_interval:
            ax.fill_between(forecast_ci.index, forecast_ci['mean_ci_lower'], forecast_ci['mean_ci_upper'], color='gray', alpha=0.2)

    if add_forecast_start_line and plot_type != "Historical":
        ax.axvline(x=2022.5, color='black', linestyle='--', linewidth=1, label='Forecast Start')
        ax.axvline(x=2050.5, color='red', linestyle='--', linewidth=1, label='Cop28 Agreement')
    ax.set_title(f'{variable} Production ({plot_type})', fontsize=16, fontweight='bold')
    ax.set_ylabel('Production (TWh)', fontsize=14)
    ax.set_xlabel('Year', fontsize=14)
    ax.legend()
    ax.grid(True, linestyle='--', which='both', color='grey', alpha=0.5)
    ax.set_ylim(bottom=0)

    return max_value

def plot_data_stacked_bar(df, forecast_results, forecast_keys, variable, plot_type, ax):
    """
    Plot stacked bar chart for data and forecasts on a matplotlib axis.

    Args:
        df (pd.DataFrame): Data frame containing the data.
        forecast_results (dict): Forecast results.
        forecast_keys (list): List of forecast keys.
        variable (str): Variable to plot.
        plot_type (str): Type of plot ("Historical", "Forecast", "Both").
        ax (matplotlib.axes.Axes): Matplotlib axis to plot on.

    Returns:
        float: Maximum value in the plotted data.
    """
    combined_data = pd.DataFrame()

    for forecast_key in forecast_keys:
        forecast = forecast_results[forecast_key]
        country = forecast['country']
        historical_data = df[(df['Country'] == country) & (df['Date'] <= 2022)][['Date', variable]].set_index('Date')
        forecast_values = forecast['forecast_values'] if plot_type != "Historical" else None

        temp_combined_data = pd.DataFrame(index=range(int(historical_data.index.min()), forecast['forecast_until_year'] + 1))
        if plot_type == "Historical" or plot_type == "Both":
            temp_combined_data.loc[historical_data.index, variable] = historical_data[variable]

        if forecast_values is not None and (plot_type == "Forecast" or plot_type == "Both"):
            temp_combined_data.loc[forecast_values.index, variable] = forecast_values.values

        combined_data[country] = temp_combined_data[variable]

    combined_data = combined_data.fillna(0)

    ax.clear()

    bottom = pd.Series([0] * len(combined_data.index), index=combined_data.index)
    colors = plt.cm.tab20(np.linspace(0, 1, len(forecast_keys)))
    max_value = combined_data.sum(axis=1).max()

    for i, forecast_key in enumerate(forecast_keys):
        country = forecast_results[forecast_key]['country']
        ax.bar(combined_data.index, combined_data[country], bottom=bottom, color=colors[i], label=country)
        bottom += combined_data[country]

    if plot_type != "Historical":
        ax.axvline(x=2022.5, color='black', linestyle='--', linewidth=1, label='Forecast Start')
        ax.axvline(x=2050.5, color='red', linestyle='--', linewidth=1, label='Cop28 Agreement')

    ax.set_title(f'{variable} Production ({plot_type})', fontsize=16, fontweight='bold')
    ax.set_ylabel('Production (TWh)', fontsize=14)
    ax.set_xlabel('Year', fontsize=14)
    ax.legend()
    ax.grid(True, linestyle='--', which='both', color='grey', alpha=0.5)
    ax.set_ylim(bottom=0)

    return max_value