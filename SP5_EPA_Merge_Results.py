import matplotlib.pyplot as plt
from pandas import DataFrame
import pandas as pd
import statsmodels.graphics.api as smg
import statsmodels.api as sm
import numpy as np
import warnings
from sklearn.metrics import mean_squared_error
from math import sqrt
from scipy.constants import g as gravity
from scipy.constants import Avogadro as avogadro

def display():
    av = avogadro  # 6.02214 * pow(10, 3)
    grav = gravity  # 9.8 Newton
    surface_pressure = 9.96921e+36  # initialization value from Netcdf files (variable: FillValue = 9.96921e+36)
    air_mass_kg = 0.0289654  # constant from : (https://en.wikipedia.org/wiki/Density_of_air)
    multiplication_factor_to_convert_to_molecules_percm2 = 6.022141E19
    november = 11
    december = 12
    ################################# Reading OGC standardized json files ####################################
    SP5 = input("Enter Sentinel-5P JSON-File Path:")
    EPA = input("Enter EPA JSON-File Path:")
    series_sp5 = pd.read_json(SP5)
    series_epa = pd.read_json(EPA)
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
    # convert string pollutant value to numeric
    json_to_dataframe_epa.Pollutant_Value = pd.to_numeric(json_to_dataframe_epa.Pollutant_Value)
    # epa data in hours
    json_to_dataframe_epa = json_to_dataframe_epa.set_index("Date_Value")

    #####################################Convert Sentinel 5-P timeseries Data to Dataframes ############################
    for series_name in series_sp5:
        pollutant_name = series_name
    var_sp5 = series_sp5[pollutant_name]
    time_array_sp5 = []
    air_quality_value_sp5 = []
    for key in var_sp5.keys():
        for (subkey, value) in zip(var_sp5[key].keys(), var_sp5[key].values()):
            if (subkey == "time"):
                time_array_sp5.append(value["instant"])
            elif (subkey == "surface_pressure"):
                surface_pressure = value["value"]
            elif (subkey == "value"):
                if (value != ""):
                    ##### Unit Conversion of Data from mol/m2 to ppb following TOBIAS criteria ########
                    ############ Link (https://search.proquest.com/docview/2117060744 #################
                    air_column = (float(surface_pressure) * avogadro) / (gravity * air_mass_kg)
                    value = multiplication_factor_to_convert_to_molecules_percm2 * float(value) / air_column / 1E9
                air_quality_value_sp5.append(value)

    data_sp5 = {
        'Date_Value': time_array_sp5,
        'Pollutant_Value': air_quality_value_sp5
    }
    json_to_dataframe_sp5 = DataFrame(data_sp5, columns=['Date_Value', 'Pollutant_Value'])
    json_to_dataframe_sp5.Date_Value = pd.to_datetime(json_to_dataframe_sp5.Date_Value, utc=True)
    json_to_dataframe_sp5.Date_Value = pd.to_datetime(json_to_dataframe_sp5.Date_Value, unit="s")
    # convert string pollutant value to numeric
    json_to_dataframe_sp5.Pollutant_Value = pd.to_numeric(json_to_dataframe_sp5.Pollutant_Value)
    # s5p one value daily in seconds
    json_to_dataframe_sp5 = json_to_dataframe_sp5.set_index("Date_Value").resample('D').mean()

    ############################ THE MERGE OF THE Sentinel5-P and EPA DATASETS########################################################
    combined_dataframe = json_to_dataframe_sp5.combine_first(json_to_dataframe_epa).sort_values(
        'Date_Value')  # sorted and null in SP5 is filled with values from EPA
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
    #smg.tsa.plot_acf(series_1.Pollutant_Value, lags=28, ax=axes[0])
    smg.tsa.plot_acf(series_1.Pollutant_Value.diff().dropna(), lags=28, ax=axes[0])
    smg.tsa.plot_acf(series_1.Pollutant_Value.diff().diff().dropna(), lags=28, ax=axes[1])
    smg.tsa.plot_acf(series_1.Pollutant_Value.diff().diff().diff().dropna(), lags=28, ax=axes[2])
    plt.show()
    ##################### To be sure there are no invalid values and to drop them if exist##############################
    series_1[~series_1.isin([np.nan, np.inf, -np.inf]).any(1)]
    series_1.replace([np.inf, -np.inf], np.nan).dropna(axis=1)
    model = sm.tsa.AR(series_1.Pollutant_Value.dropna())
    result = model.fit(288)  # fit to 3 days as the frequency is D
    ############ Use the result of Durbin Watson to show that there is no significant auto-correlation #################
    sm.stats.durbin_watson(result.resid)
    print("Durbin Watson")
    print(sm.stats.durbin_watson(result.resid))
    # plot the result of Durbin Watson to show that there is no significant auto-correlation
    fig, ax = plt.subplots(1, 1, figsize=(8, 3))
    # smg.tsa.plot_acf(result.resid, lags=72, ax=ax) for hours
    smg.tsa.plot_acf(result.resid, lags=27, ax=ax)
    plt.show()
    ####################################Air Quality Forecast############################################################
    air_quality_forecast = result.predict(start=288, end=480,
                                          dynamic=False)  # try for the modelling
    fig, ax = plt.subplots(1, 1, figsize=(12, 4))
    ax.plot(series_1.index.values[-288:], series_1.Pollutant_Value.values[-288:], label="train data")
    ax.plot(series_2.index.values[:288], series_2.Pollutant_Value.values[:288], label="actual data")
    ax.plot(pd.date_range("2018-12-01 00:00:00+00:00", "2018-12-03 00:00:00+00:00", freq="15min").values,
            air_quality_forecast,
            label="predicted outcome")
    sample = series_2[
             '2018-12-01 00:00:00+00:00':'2018-12-03 00:00:00+00:00']
    ####################################Air Quality Forecast############################################################
    print("RMSE")
    print(sqrt(mean_squared_error(sample, air_quality_forecast)))
    #####################################Check Autocorrelation SP5 and EPA##############################################
    ax.legend()
    plt.show()
    print("Correlation sp5 and epa")
    print(json_to_dataframe_sp5.corrwith(json_to_dataframe_epa, method='pearson'))
if __name__ == '__main__':
    warnings.filterwarnings('ignore', 'statsmodels.tsa.ar_model.AR', FutureWarning)
    NO2_file_path = display()
