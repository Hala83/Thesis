# This code search in the netcdf for values near a required location (UCD)
# If the required range (location +delta or location - delta) for the location is not found the data is not saved .
# A folder has group of 60 Netcdf files is passed for the code
# Creation for each Netcdf file a JSON file with same name if that JSON file doesn't exist already
# Extracting of attributes and depending on the pollutant the parsing is different as not all Netcdf files are unified
3 Scaneline and ground_pixel are used to search and find the location, time and value of the pollutant
import json
from netCDF4 import Dataset
from collections import OrderedDict
import pandas as pd
from datetime import datetime
from datetime import timedelta
import glob
import time
import tqdm
import os


def read_pollution_db(latitude, longitude, delta_lat, delta_long):

    for nc_file in glob.glob("/merged_files/*.nc"):
        try:
            start_file_time = time.time()
            assumed_number = 1
            nc_data = Dataset(nc_file)
            new_file_name = os.path.splitext(os.path.basename(nc_file))[0]
            output_file_path = "/merged_files/" + new_file_name + ".json"

            # skip if file exists
            if os.path.exists(output_file_path):
                print("File already exists skipping {}".format(output_file_path))
                continue

            print("Writing to file: {}".format(output_file_path))

            vertical_column_group = ""
##############################Extracting some attributes from the NetCDF file###########################################
            with nc_data as ncFile:

                start = getattr(ncFile, 'time_coverage_start')
                end = getattr(ncFile, 'time_coverage_end')
                ID = getattr(ncFile, 'id')
                total_column_name = ""

                net_cdf_product = ncFile["PRODUCT"]

                pollutant_name_start_indx = str(ID).find('__')
                pollutant_name_end_indx = str(ID).find('___')
                pollutant_name = ID[(pollutant_name_start_indx + 2):(pollutant_name_end_indx)]
#####################Depending on each pollutant the parsing is different ##############################################
                if pollutant_name == "CO":
                    total_column_name = 'carbonmonoxide_total_column'
                    vertical_column_group = "PRODUCT"
                    uom_from_file = ncFile[vertical_column_group].variables[total_column_name].units
                elif pollutant_name == "SO2":
                    total_column_name = 'sulfurdioxide_total_vertical_column'
                    vertical_column_group = "PRODUCT"
                    uom_from_file = ncFile[vertical_column_group].variables[total_column_name].units
                elif pollutant_name == "NO2":
                    total_column_name = 'nitrogendioxide_total_column'
                    vertical_column_group = "DETAILED_RESULTS"
                    uom_from_file = net_cdf_product["SUPPORT_DATA"][vertical_column_group].variables[
                        total_column_name].units
                elif pollutant_name == "O3":
                    total_column_name = 'ozone_total_vertical_column'
                    vertical_column_group = "PRODUCT"
                    uom_from_file = ncFile[vertical_column_group].variables[total_column_name].units
                lat_uom = net_cdf_product.variables['latitude'].units
                long_uom = net_cdf_product.variables['longitude'].units
                surface_pressure_uom = net_cdf_product["SUPPORT_DATA"]["INPUT_DATA"].variables[
                    "surface_pressure"].units
                scanline_count = (net_cdf_product.dimensions['scanline'].size)
                ground_pixel_count = (net_cdf_product.dimensions['ground_pixel'].size)
                pollutant_value = 0
                ntcdfValueArray = []

                ground_pixel_start_index = 0
###############################Checking that the required latitude is found in the file#################################
                for scanline_index in tqdm.tqdm(range(0, scanline_count)): # The progress is being printed using tqdm loop
                    #### for every scaneline get min and max latitude
                    #### the latitude is lees than min or greater than max then skip this scanline
                    #### This minimizes the size of the json file and guarantees that it has the UCD location
                    min_lat = net_cdf_product.variables['latitude'][0][scanline_index].min()
                    max_lat = net_cdf_product.variables['latitude'][0][scanline_index].max()
                    if latitude < min_lat or latitude > max_lat:
                        continue
###############################Extracting time of each reading #########################################################
                    monitoring_time = net_cdf_product.variables['time_utc'][0][scanline_index]
                   #### If monitoring time is empty calculate it from the start and add to it the scanline_index in seconds
                    ### and then add the time zone parameters the T and the Z
                    if monitoring_time == "":  # add the time zone parameters the T and the Z
                        temp_monitoring_time = pd.to_datetime(start) + timedelta(seconds=scanline_index)
                        monitoring_time = str(temp_monitoring_time)
                        monitoring_time = str(monitoring_time.replace(" ", 'T'))  # replace the space with (T)
                        monitoring_time = str(monitoring_time.__add__('Z'))

                    first_ground_pixel = None
#######################Extracting the latitude and longitude values for all the values after guaranteeing that the required lat. is in the file######
                    for ground_pixel_index in range(ground_pixel_start_index, ground_pixel_count):
                        lat_approximated_value = net_cdf_product.variables['latitude'][0][scanline_index][
                            ground_pixel_index]
                        lon_approximated_value = net_cdf_product.variables['longitude'][0][scanline_index][
                            ground_pixel_index]

                        # longitudes are sorted, so if I passed my range then no need to keep processing
                        if lon_approximated_value > longitude + delta_lat:
                            break

                        # all values outside my range I don't need them
                        if lat_approximated_value < latitude - delta_lat or lat_approximated_value > latitude + delta_lat or lon_approximated_value < longitude - delta_lat:
                            continue

                        if not first_ground_pixel:
                            first_ground_pixel = ground_pixel_index

                        surface_pressure = \
                        net_cdf_product["SUPPORT_DATA"]["INPUT_DATA"].variables["surface_pressure"][0][
                            scanline_index][ground_pixel_index]
                        if (pollutant_name == "NO2"):
                            pollutant_value = \
                            net_cdf_product["SUPPORT_DATA"][vertical_column_group].variables[total_column_name][0][
                                scanline_index][ground_pixel_index]
                        else:
                            pollutant_value = \
                            ncFile[vertical_column_group].variables[total_column_name][0][scanline_index][
                                ground_pixel_index]
                        if (pollutant_value != "--"):
                            pollutant_value = pollutant_value * assumed_number

                            ntcdfValueArray.append({
                                "time": {"instant": str(monitoring_time)},
                                "surface_pressure": {"value": str(surface_pressure),
                                                     "uom": str(surface_pressure_uom)},
                                "Longitude": {"value": float(lon_approximated_value), "uom": str(long_uom)},
                                "Latitude": {"value": float(lat_approximated_value), "uom": str(lat_uom)},
                                "uom": str(uom_from_file), "value": str(pollutant_value),
                                "scanline": scanline_index,
                                "ground_pixel": ground_pixel_index
                            })

                    # for next scan line iteration use this ground pixel to start from
                    if first_ground_pixel:
                        ground_pixel_start_index = first_ground_pixel
                        if ground_pixel_start_index >= ground_pixel_count - 1:
                            ground_pixel_start_index = 0
                            print("Restarting ground pixel at scanline {}".format(scanline_index))

            pollutantValues = {pollutant_name: ntcdfValueArray}
            with open(output_file_path, 'w') as outfile:
                outfile.write(json.dumps(OrderedDict(pollutantValues), indent=2, sort_keys=True))

            end_file_time = time.time()
            print("{} {}".format(nc_file, end_file_time - start_file_time))
        except Exception as e:
            print("Error processing file", e)


if __name__ == '__main__':
    print("Procesing started: {}".format(datetime.now()))
    read_pollution_db(53.3067, -6.221, 5, 5)
    print("Processing ended: {}".format(datetime.now()))