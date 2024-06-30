import pandas as pd
from statsmodels.tsa.stattools import adfuller

def perform_adf_test(data):
    """
    Perform ADF test on the original data.
    
    Args:
        data (pd.DataFrame): Data for the ADF test.

    Returns:
        pd.DataFrame: ADF test results.
    """
    if data.nunique().values[0] == 1:
        return pd.DataFrame([{
            'ADF Statistic': None,
            'p-value': None,
            'Num Lags': None,
            'Num Observations': None,
            '1%': None,
            '5%': None,
            '10%': None,
            'Stationary': 'No',
            'Error': 'Input data is constant'
        }])

    adf_result = adfuller(data)
    p_value = adf_result[1]
    stationary = 'Yes' if p_value <= 0.05 else 'No'
    
    result = {
        'ADF Statistic': adf_result[0],
        'p-value': p_value,
        'Num Lags': adf_result[2],
        'Num Observations': adf_result[3],
        '1%': adf_result[4]['1%'],
        '5%': adf_result[4]['5%'],
        '10%': adf_result[4]['10%'],
        'Stationary': stationary
    }

    return pd.DataFrame([result])
