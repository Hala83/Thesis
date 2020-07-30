import json
import pandas as pd
import numpy as np
import glob
from collections import OrderedDict
# In this program we are searching in Sentinel5-P Json formatted files for data in the location of UCD
# UCD : 53.3067° N, 6.2210° W  location 1 :Stillorgan Road, Booterstown, Dublin, D04 F438
# Booterstown Dublin Ireland
# To merge the ouptut file with EPA and in-situ sensors datasets
# The nearest input data to UCD location
# The output file will have an entry daily for air quality
def display():
    #################################Choose Output file of merged Data##################################################
    outputFilePath = "/THE_FINAL/SP5_CO.json"
    #('C:/NC/SentinelData/THE_FINAL/SP5_NO2.json')
    merged_array = []
    pollutant_name = ""
    ################################# Reading Data in OGC standardized json file ####################################
    for file_name in glob.glob("/processed_json/*.json"):
        series = pd.read_json(file_name)
        for series_name in series:
            pollutant_name = series_name ##reading pollutant name
        longitude = 0.0
        latitude = 0.0
        surface_pressure = 0.0
        least_long = 300
        least_lat = 300
        air_quality = 0.0
        eucledean_min_dist = 0
        air_quality_uom = ""
        min_long = 0.0
        min_lat = 0.0
        optimum_value = 0
        dist_min = 100
        var = series[pollutant_name]
        for key in var.keys():
            iterate = 0
            dist_min = 100
            for (subkey, value) in zip(var[key].keys(), var[key].values()):
                if (subkey == "time"):
                    time = value["instant"]
                elif (subkey == "surface_pressure"):
                    surface_pressure = value["value"]
                    surface_pressure_uom = value["uom"]
                elif (subkey == "Latitude"):  # searching for nearest latitude
                    if (51.0 < value["value"] < 54.0):
                        latitude = value["value"]
                        iterate = iterate + 1
                elif (subkey == "Longitude"): # searching for nearest longitude
                    if (-8.0 <= value["value"] <= -5.0):
                        longitude = value["value"]
                        iterate = iterate + 1
                elif (subkey == "uom"):
                    air_quality_uom = value

                elif (subkey == "value"):
                    air_quality = value

            if iterate == 2:
                a = np.array((latitude, longitude))
                b = np.array((53.350140, -6.266155)) # Location of UCD
                dist = np.linalg.norm(a - b)
                ############ Searching for nearest Point ###############
                if dist < dist_min: # Eucledean distance in file to UCD
                    dist_min = dist
                    min_long = longitude
                    min_lat = latitude
                    optimum_value = air_quality
                    optimum_time = time
                    eucledean_min_dist = dist_min
##########################Making new file with one entry daily for air quality##########################################
        if optimum_value != 0:
            merged_array.append(
                {"uom": str(air_quality_uom), "value": str(optimum_value), "optimum_dist": str(eucledean_min_dist),
                "time": {"instant": str(optimum_time)},"surface_pressure":{"value":surface_pressure,"uom":surface_pressure_uom}})
    pollutantValues = {pollutant_name: merged_array}
    outfile = open(outputFilePath, 'w')
    outfile.write(json.dumps(OrderedDict(pollutantValues), indent=4, sort_keys=True))

if __name__ == '__main__':

    NO2_file_path = display()

