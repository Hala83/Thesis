# This code merge standardised datasets
# This code was used to compare different fusion criteria and check which is the best
# According to the desired test the frequency should be changed and the order of datasets in the merge should be changed too
# Model and Predict results
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
    multiplication_factor_to_convert_to_molecules_percm2 = 6.022141E19  # Value from Netcdf file
    november = 11
    december = 12
    ################################# Reading OGC standardized json files ####################################
    SP5 = input("Enter Sentinel-5P JSON-File Path:")
    SCK = input("Enter SCK JSON-File Path:")
    EPA = input("Enter EPA JSON-File Path:")
    series_sp5 = pd.read_json(SP5)
    series_sck = pd.read_json(SCK)
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
            if subkey == "time":
                time_array_epa.append(value["instant"])
            elif subkey == "value":
                air_quality_value_epa.append(value)
    data_EPA = {
        'Date_Value': time_array_epa,
        'Pollutant_Value': air_quality_value_epa
    }
    json_to_dataframe_epa = DataFrame(data_EPA, columns=['Date_Value', 'Pollutant_Value'])
    json_to_dataframe_epa.Date_Value = pd.to_datetime(json_to_dataframe_epa.Date_Value, utc=True)
    json_to_dataframe_epa.Date_Value = pd.to_datetime(json_to_dataframe_epa.Date_Value, unit="s")
    #convert string pollutant value to numeric
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
            elif(subkey == "surface_pressure"):
                surface_pressure = value["value"]
            elif (subkey == "value"):
                if(value != ""):
                    ##### Unit Conversion of Data from mol/m2 to ppb following TOBIAS criteria ########
                    ############ Link (https://search.proquest.com/docview/2117060744 #################
                    air_column = (float(surface_pressure) * avogadro) / (gravity * air_mass_kg)
                    value = multiplication_factor_to_convert_to_molecules_percm2 * float(value) / air_column / 1E9
                    ##### Unit Conversion of Data from mol/m2 to ppb following Marios criteria ########
                    ############# Link (http://ikee.lib.auth.gr/record/308538/files/GRI-2019-25816.pdf)#################
                    #value = float(value) * multiplication_factor_to_convert_to_molecules_percm2 / 2.45
                    ##No_Unit _conversion
                    #value = value

                air_quality_value_sp5.append(value)
    data_sp5 = {
        'Date_Value': time_array_sp5,
        'Pollutant_Value': air_quality_value_sp5
    }
    json_to_dataframe_sp5 = DataFrame(data_sp5, columns=['Date_Value', 'Pollutant_Value'])
    json_to_dataframe_sp5.Date_Value = pd.to_datetime(json_to_dataframe_sp5.Date_Value, utc=True)
    json_to_dataframe_sp5.Date_Value = pd.to_datetime(json_to_dataframe_sp5.Date_Value, unit="s")
    #convert string pollutant value to numeric
    json_to_dataframe_sp5.Pollutant_Value = pd.to_numeric(json_to_dataframe_sp5.Pollutant_Value)
    # s5p one value daily in seconds
    json_to_dataframe_sp5 = json_to_dataframe_sp5.set_index("Date_Value").resample('D').mean()

    #####################################Convert SCK timeseries Data to Dataframes #####################################
    time_array_sck = []
    air_quality_value_sck = []
    for series_name in series_sck:
        pollutant_name = series_name
    var_sck = series_sck[pollutant_name]
    for key_sck in var_sck.keys():
        for (subkey_sck, value_sck) in zip(var_sck[key_sck].keys(),  var_sck[key_sck].values()):
            if subkey_sck == "time":
                time_array_sck.append(value_sck["instant"])
            elif subkey_sck == "value":
                if value_sck !="":
                    value_sck = (float(value_sck))
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
    # SCK in minutes
    json_to_dataframe_sck = json_to_dataframe_sck.set_index("Date_Value")
    ############################ THE MERGE OF THE THREE DATASETS########################################################
    # According to the desired test the frequency should be changed and the order of datasets in the merge should be changed too
    # old_combined_dataframe = json_to_dataframe_epa.combine_first(json_to_dataframe_sck).sort_values(
    #     'Date_Value')  # sorted and null in epa is filled with values from sck FINAL TRIAL
    # combined_dataframe = json_to_dataframe_sp5.combine_first(old_combined_dataframe).sort_values('Date_Value') #FINAL TRIAL
    old_combined_dataframe = json_to_dataframe_sp5.combine_first(json_to_dataframe_epa).sort_values(
        'Date_Value')  # sorted and null in epa is filled with values from sck FINAL RESULT
    combined_dataframe = old_combined_dataframe.combine_first(json_to_dataframe_sck).sort_values('Date_Value') # FINAL RESULT
    print("SP5 + EPA + SCK std deviation = ")
    print(str(combined_dataframe.std))
    print("Correlation (SP5 + EPA) + SCK")
    #print(old_combined_dataframe.corrwith(combined_dataframe, method='pearson'))

    #################################
    # print("Correlation SP5 and EPA")
    # print(json_to_dataframe_sp5.corrwith(json_to_dataframe_epa, method='pearson'))
    #################################
    # print("Correlation EPA and SCK")
    # print(json_to_dataframe_epa.corrwith(json_to_dataframe_sck, method='pearson'))
    #
    #
    # print("Correlation SP5 and SCK")
    # print(json_to_dataframe_sp5.corrwith(json_to_dataframe_sck, method='pearson'))
    #####

    # #combined_dataframe = json_to_dataframe_epa.combine_first(json_to_dataframe_sck).sort_values(
    #  'Date_Value')  # sorted and null in epa is filled with values from sck
    #combined_dataframe = json_to_dataframe_epa.join(json_to_dataframe_sck, how='outer')
    #################################################Write Merged Data to File##########################################
    outfile = open(output, 'w')
    combined_dataframe.to_csv(outfile, sep='\t')
    #µg/m3= (ppb)*(12.187)*(M) / (273.15 + °C) where M is the molecular weight of the gaseous pollutant. An atmospheric pressure of 1 atmosphere is assumed.
    #The conversion assumes an ambient pressure of 1 atmosphere and a temperature of 25 degrees celsius
    #SO2 1 ppb = 2.62 µg/m3
    # NO2 1 ppb = 1.88 µg/m3
    # NO 1 ppb = 1.25 µg/m3
    # O3 1 ppb = 2.00 µg/m3
    # CO 1 ppb = 1.145 µg/m3
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
    result = model.fit(3000)  # fit to 3 days as the frequency for SCK
    ############ Use the result of Durbin Watson to show that there is no significant auto-correlation #################
    sm.stats.durbin_watson(result.resid)
    print("DURBIN WATSON")
    print(sm.stats.durbin_watson(result.resid))
    fig, ax = plt.subplots(1, 1, figsize=(8, 3))
    smg.tsa.plot_acf(result.resid, lags=27, ax=ax)
    plt.show()
    ####################################Air Quality Forecast############################################################
    air_quality_forecast = result.predict(start='2018-12-01 00:00:00+00:00', end='2018-12-03 00:00:00+00:00',
                                          dynamic=False)  #Period for prediction
    fig, ax = plt.subplots(1, 1, figsize=(12, 4))
    ax.plot(series_1.index.values[-3000:], series_1.Pollutant_Value.values[-3000:], label="train data")
    ax.plot(series_2.index.values[:3000], series_2.Pollutant_Value.values[:3000], label="actual data")
    ax.plot(pd.date_range("2018-12-01 00:00:00+00:00", "2018-12-03 00:00:00+00:00", freq="min").values,
            air_quality_forecast,
            label="predicted outcome")
    sample = series_2[
             '2018-12-01 00:00:00+00:00':'2018-12-03 00:00:00+00:00']
    ####################################Air Quality Forecast Error######################################################
    print("RMSE:")
    print(sqrt(mean_squared_error(sample, air_quality_forecast))) ## Calculating the prediction error
    ax.legend()
    plt.show()


if __name__ == '__main__':

    warnings.filterwarnings('ignore', 'statsmodels.tsa.ar_model.AR', FutureWarning)
    display()




