import matplotlib.pyplot as plt
from pandas import DataFrame
import pandas as pd
import statsmodels.graphics.api as smg
import statsmodels.api as sm
import numpy as np
import warnings
from sklearn.metrics import mean_squared_error
from math import sqrt

def display():
    november = 11
    december = 12
    ################################# Reading OGC standardized json files ####################################
    series = pd.read_json('pollutant_O3_2018.json') # Durbin watson = 3.0134 RMSE = 90.1668
    #####################################Convert EPA timeseries Data to Dataframes #####################################
    time_array = []
    air_quality_value = []
    air_quality_uom_value = []
    for key in series.Ozone.keys():
        for value in series.Ozone[key].values():
            time_array.append(value["instant"])
            break
    skip_time = 0
    # searching for pollutant value
    for key in series.Ozone.keys():
        for value in series.Ozone[key].values():
            if(skip_time == 0):
                skip_time = 1
            elif(skip_time == 1):
                air_quality_value.append(value)
                skip_time = 2
            elif (skip_time == 2):
                air_quality_uom_value.append(value)
                skip_time = 0

    data = {
        'Date_Value': time_array,
        'Pollutant_Value': air_quality_value
    }
    json_to_dataframe = DataFrame(data, columns=['Date_Value', 'Pollutant_Value'])
    json_to_dataframe.Date_Value = pd.to_datetime(json_to_dataframe.Date_Value, utc=True)
    json_to_dataframe.Date_Value = pd.to_datetime(json_to_dataframe.Date_Value, unit="s")
    #convert string pollutant value to numeric
    json_to_dataframe.Pollutant_Value = pd.to_numeric(json_to_dataframe.Pollutant_Value)
    json_to_dataframe = json_to_dataframe.set_index("Date_Value")
    ###########################################Plot of autocorrelation of dataset ######################################
    series_1 = json_to_dataframe[json_to_dataframe.index.month == november]
    print("series_1")
    print(series_1.keys())
    print(series_1)
    series_2 = DataFrame(json_to_dataframe[json_to_dataframe.index.month == december])
    #subplots takes number of rows and number of column in the output grid
    fig, axes = plt.subplots(1, 3, figsize=(12, 3))
    # in the json file used from EPA after the mean operation every day has 1 entry so each month has 30 entry no more than 31 max
    # method dropna() allows the user to analyze and drop Rows/Columns with Null values in different ways
    #Pandas dataframe.diff() is used to find the first discrete difference of objects over the given axis. We can provide a period value to
    #shift for forming the difference.It is used to check the auto correlation in higher order.
    #Syntax: DataFrame.diff(periods=1, axis=0)
    # lags = 28 is how many timesteps to be included in the plot
    # The auto correlation functions for the pollution and its first ,second and third order differences
    # axes parameter is used for number of graphs drawn ..first plot in axes 0, second in axes 1,..etc
    # To make an AR model it is important to check that it doesn't have auto correlation or autocorrelation decay
    # It should be to stationary process
    # plot with increasingly time delays
    smg.tsa.plot_acf(series_1.Pollutant_Value.diff().dropna(), lags=28, ax=axes[0])
    smg.tsa.plot_acf(series_1.Pollutant_Value.diff().diff().dropna(), lags=28, ax=axes[1])
    smg.tsa.plot_acf(series_1.Pollutant_Value.diff().diff().diff().dropna(), lags=28, ax=axes[2])
    plt.show()
    ##If we can draw like histogram for data then their is a correlation (realtion) between data and previous one. Taking the difference between of
    # a time series is often a useful way of detrending it and eleminating correlation
    # as the dependency between data decreases in higher order this suggest the use of AR model
    ##################### To be sure there are no invalid values and to drop them if exist##############################
    series_1[~series_1.isin([np.nan, np.inf, -np.inf]).any(1)]
    series_1.replace([np.inf, -np.inf], np.nan).dropna(axis=1)
    model = sm.tsa.AR(series_1.Pollutant_Value.dropna())
    result = model.fit(288)
    ############ Use the result of Durbin Watson to show that there is no significant auto-correlation #################
    #Durbin-Watson statistical test to test for stationary in a time series. Valeu close to 2 means time series do not have
    #remaining auto-correlation
    sm.stats.durbin_watson(result.resid)
    print("DURBIN WATSON")
    print(sm.stats.durbin_watson(result.resid))
    #plot the result of Durbin Watson to show that there is no significant auto-correlation
    fig, ax = plt.subplots(1,1, figsize=(8, 3))
    smg.tsa.plot_acf(result.resid, lags=288, ax=ax)
    plt.show()
    ####################################Air Quality Forecast############################################################
    #if the Durbin-Watson close to 2 and the graph doesn't show auto-correlation then we can predict
    air_quality_forecast = result.predict(start='2018-12-01 00:00:00+00:00', end='2018-12-03 00:00:00+00:00', dynamic=False)
    fig, ax = plt.subplots(1,1, figsize=(12,4))
    ax.plot(series_1.index.values[-288:], series_1.Pollutant_Value.values[-288:], label="train data")
    ax.plot(series_2.index.values[:288], series_2.Pollutant_Value.values[:288], label="actual data")
    ax.plot(pd.date_range("2018-12-01 00:00:00+00:00", "2018-12-03 00:00:00+00:00", freq="H").values, air_quality_forecast,
            label="predicted outcome")
    ax.legend()
    plt.show()
    sample = series_2['2018-12-01 00:00:00+00:00':'2018-12-03 00:00:00+00:00']
    ####################################Air Quality Forecast Error######################################################
    print("RMSE:")
    print(sqrt(mean_squared_error(sample, air_quality_forecast)))


if __name__ == '__main__':
    warnings.filterwarnings('ignore', 'statsmodels.tsa.ar_model.AR', FutureWarning)
    display()
