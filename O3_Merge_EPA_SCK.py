# This code merge the standardised EPA and SCK datasets
# Modelling of merged datasets
# Forecast of merged datasets

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
    ################################# Reading OGC standardized json files ##############################################
    sck = input("Enter sck Path:")
    epa = input("Enter epa Path:")
    series_sck = pd.read_json(sck)
    series_epa = pd.read_json(epa)
    #################################Choose Output file of merged Data##################################################
    output = input("Enter Merged Output File Path:")
    #####################################Convert EPA timeseries Data to Dataframes #####################################
    for series_name in series_epa:
        pollutant_name = series_name
    var_epa = series_epa[pollutant_name]
    time_array_epa = []
    air_quality_value_epa = []
    for key in var_epa.keys():
        for (subkey, value) in zip(var_epa[key].keys(), var_epa[key].values()):
            if (subkey == "time"):
                time_array_epa.append(value["instant"])
            elif (subkey == "value"):
                air_quality_value_epa.append(value)

    data_epa = {
        'Date_Value': time_array_epa,
        'Pollutant_Value': air_quality_value_epa
    }
    json_to_dataframe_epa = DataFrame(data_epa, columns=['Date_Value', 'Pollutant_Value'])
    json_to_dataframe_epa.Date_Value = pd.to_datetime(json_to_dataframe_epa.Date_Value, utc=True)
    json_to_dataframe_epa.Date_Value = pd.to_datetime(json_to_dataframe_epa.Date_Value, unit="s")
    #convert string pollutant value to numeric
    json_to_dataframe_epa.Pollutant_Value = pd.to_numeric(json_to_dataframe_epa.Pollutant_Value)
    # epa in hours
    json_to_dataframe_epa = json_to_dataframe_epa.set_index("Date_Value")
    #####################################Convert SCK timeseries Data to Dataframes #####################################
    time_array_sck = []
    air_quality_value_sck = []
    for series_name in series_sck:
        pollutant_name = series_name
    var_sck = series_sck[pollutant_name]
    for key_sck in  var_sck.keys():
        for (subkey_sck, value_sck) in zip( var_sck[key_sck].keys(),  var_sck[key_sck].values()):
            if (subkey_sck == "time"):
                time_array_sck.append(value_sck["instant"])
            elif(subkey_sck == "value"):
    ##########################################Unit Conversion###########################################################
                #unify the unit from ppb to ug/m3
                # µg/m3= (ppb)*(12.187)*(M) / (273.15 + °C) where M is the molecular weight of the gaseous pollutant. An atmospheric pressure of 1 atmosphere is assumed.
                # The conversion assumes an ambient pressure of 1 atmosphere and a temperature of 25 degrees celsius
                #for O3 DIVIDE BY 2.0
                if(value_sck !=""):
                    value_sck = (float(value_sck))/2.0 # for OZONE
                    #value_sck = (float(value_sck))
                air_quality_value_sck.append(value_sck)

    data = {
        'Date_Value': time_array_sck,
        'Pollutant_Value': air_quality_value_sck
    }
    json_to_dataframe_sck = DataFrame(data, columns=['Date_Value', 'Pollutant_Value'])
    json_to_dataframe_sck.Date_Value = pd.to_datetime(json_to_dataframe_sck.Date_Value, utc=True)
    json_to_dataframe_sck.Date_Value = pd.to_datetime(json_to_dataframe_sck.Date_Value, unit="s")
    #convert string pollutant value to numeric
    json_to_dataframe_sck.Pollutant_Value = pd.to_numeric(json_to_dataframe_sck.Pollutant_Value)
    json_to_dataframe_sck = json_to_dataframe_sck.set_index("Date_Value")  # sck in minutes

    ############################ THE MERGE OF THE TWO DATASETS##########################################################
    combined_dataframe = json_to_dataframe_epa.combine_first(json_to_dataframe_sck).sort_values(
        'Date_Value')  # sorted and null in epa is filled with values from sck
    print("epa + sck std deviation = ")
    print(str(combined_dataframe.std))
    #################################
    print("Correlation epa and sck")
    print(json_to_dataframe_epa.corrwith(json_to_dataframe_sck, method='pearson')) # NO2: r =  0.246653//CO: r = 0.687883// O3: r=-0.30058
    #################################################Write Merged Data to File##########################################
    outfile = open(output, 'w')
    combined_dataframe.to_csv(outfile, sep='\t')
    ###########################################Plot of autocorrelation of merged dataset ###############################
    # lags = 28 is how many timesteps to be included in the plot
    # The auto correlation functions for the pollution and its first ,second and third order differences
    # axes parameter is used for number of graphs drawn ..first plot in axes 0, second in axes 1,..etc
    # To make an AR model it is important to check that it doesn't have auto correlation or autocorrelation decay
    # It should be to stationary process
    # plot with increasingly time delays
    series_1 = combined_dataframe[combined_dataframe.index.month == november]
    series_2 = DataFrame(combined_dataframe[combined_dataframe.index.month == december])
    fig, axes = plt.subplots(1, 3, figsize=(12, 3))
    smg.tsa.plot_acf(series_1.Pollutant_Value.diff().dropna(), lags=28, ax=axes[0])
    smg.tsa.plot_acf(series_1.Pollutant_Value.diff().diff().dropna(), lags=28, ax=axes[1])
    smg.tsa.plot_acf(series_1.Pollutant_Value.diff().diff().diff().dropna(), lags=28, ax=axes[2])
    plt.show()
    ##################### To be sure there are no invalid values and to drop them if exist##############################
    series_1[~series_1.isin([np.nan, np.inf, -np.inf]).any(1)]
    series_1.replace([np.inf, -np.inf], np.nan).dropna(axis=1)
    model = sm.tsa.AR(series_1.Pollutant_Value.dropna())
    result = model.fit(3000)  # fit to 3 days as the frequency is D worked in epa
    ############ Use the result of Durbin Watson to show that there is no significant auto-correlation #################
    sm.stats.durbin_watson(result.resid)
    print("DURBIN WATSON")
    print(sm.stats.durbin_watson(result.resid))
    fig, ax = plt.subplots(1, 1, figsize=(8, 3))
    smg.tsa.plot_acf(result.resid, lags=27, ax=ax)
    plt.show()
    ####################################Air Quality Forecast############################################################
    air_quality_forecast = result.predict(start='2018-12-01 00:00:00+00:00', end='2018-12-03 00:00:00+00:00',
                                          dynamic=False)  # try for the modelling
    fig, ax = plt.subplots(1, 1, figsize=(12, 4))
    ax.plot(series_1.index.values[-3000:], series_1.Pollutant_Value.values[-3000:], label="train data")
    ax.plot(series_2.index.values[:3000], series_2.Pollutant_Value.values[:3000], label="actual data")
    ax.plot(pd.date_range("2018-12-01 00:00:00+00:00", "2018-12-03 00:00:00+00:00", freq="min").values,
            air_quality_forecast,
            label="predicted outcome")  # for O3 for merge model
    sample = series_2[
             '2018-12-01 00:00:00+00:00':'2018-12-03 00:00:00+00:00']  # Durbon_Watson = 2.024053606297852 for O3 for modelling rmse = 15.277812286512733
    ####################################Air Quality Forecast Error######################################################
    print("RMSE")
    print(sqrt(mean_squared_error(sample, air_quality_forecast)))
    ax.legend()
    plt.show()

if __name__ == '__main__':
    #CO : s5p+ epa+sck = 2.0000077437932275 DARBI WATSON  RMSE = 0.10656768500280639
    warnings.filterwarnings('ignore', 'statsmodels.tsa.ar_model.AR', FutureWarning)
    NO2_file_path = display()




