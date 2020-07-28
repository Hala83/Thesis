# Code to parse any Sentinel-5P NetCDF file to standardised Json file
# Save global attributes of start and end recording time
# Extract the pollutant name from the global attribute (ID)
# Extract the pollutant value depending on its location in the file
# Extract the location of the recording of the pollutant based on the ground-pixel and scanline of the associated time
# Convert the time to ISO-8601
# If monitoring time is missing calculate it using the start time of recording and the scanline

import numpy as np
import json
from netCDF4 import Dataset
from collections import OrderedDict
import pandas as pd
from datetime import timedelta


def read_pollution_db():

    nc_file = Dataset("S5P_OFFL_L2__CO_____20181201T112749_20181201T130919_05875_01_010202_20181207T105556.nc")
    parsed_nc_file = "S5P_OFFL_L2__CO_____20181201T112749_20181201T130919_05875_01_010202_20181207T105556.json"
    vertical_column_group = ""
    with nc_file as ncFile:

        start = getattr(ncFile, 'time_coverage_start')
        end = getattr(ncFile, 'time_coverage_end')
        ID = getattr(ncFile, 'id')
        total_column_name= ""

        pollutant_name_start_indx = str(ID).find('__')
        pollutant_name_end_indx =str(ID).find('___')
        pollutant_name = ID[(pollutant_name_start_indx + 2):(pollutant_name_end_indx)]
        if(pollutant_name == "CO"):
            total_column_name = 'carbonmonoxide_total_column'
            vertical_column_group = "PRODUCT"
            uom_from_file = ncFile[vertical_column_group].variables[total_column_name].units
        elif(pollutant_name == "SO2"):
            total_column_name = 'sulfurdioxide_total_vertical_column'
            vertical_column_group = "PRODUCT"
            uom_from_file = ncFile[vertical_column_group].variables[total_column_name].units
        elif(pollutant_name == "NO2"):
            total_column_name = 'nitrogendioxide_total_column'
            vertical_column_group = "DETAILED_RESULTS"
            uom_from_file = ncFile["PRODUCT"]["SUPPORT_DATA"][vertical_column_group].variables[total_column_name].units
        elif (pollutant_name == "O3"):
            total_column_name = 'ozone_total_vertical_column'
            vertical_column_group = "PRODUCT"
            uom_from_file = ncFile[vertical_column_group].variables[total_column_name].units
        uom_from_file_lat = ncFile["PRODUCT"].variables['latitude'].units
        uom_from_file_long = ncFile["PRODUCT"].variables['longitude'].units
        uom_from_file_pressure = ncFile["PRODUCT"]["SUPPORT_DATA"]["INPUT_DATA"].variables["surface_pressure"].units
        scanline_count = (ncFile["PRODUCT"].dimensions['scanline'].size)
        ground_pixel_count = (ncFile["PRODUCT"].dimensions['ground_pixel'].size )
        latitude_list = []
        longitude_list = []
        pollutant_scanline_position = 0
        pollutant_ground_pixel_position = 0
        pollutant_value = 0
        ntcdfValueArray = []
        lat_array_values = []
        for lat_scanline_count in range(0, scanline_count):
            monitoring_time = ncFile["PRODUCT"].variables['time_utc'][0][lat_scanline_count]
            if (monitoring_time == ""):  # add the time zone parameters the T and the Z
                temp_monitoring_time = pd.to_datetime(start) + timedelta(seconds=lat_scanline_count)
                monitoring_time = str(temp_monitoring_time)
                monitoring_time = str(monitoring_time.replace(" ", 'T'))  # replace the space with (T)
                monitoring_time = str(monitoring_time.__add__('Z'))

            for lat_ground_pixel_count in range(0, ground_pixel_count):
                qa_value = float(ncFile["PRODUCT"].variables['longitude'][0][lat_scanline_count][
                                     lat_ground_pixel_count].item(0))
                if qa_value > 0.5:
                    surface_pressure = ncFile["PRODUCT"]["SUPPORT_DATA"]["INPUT_DATA"].variables["surface_pressure"][0][
                            lat_scanline_count][lat_ground_pixel_count]
                    if (pollutant_name == "NO2"):
                        pollutant_value = ncFile["PRODUCT"]["SUPPORT_DATA"][vertical_column_group].variables[total_column_name][0][
                            lat_scanline_count][lat_ground_pixel_count]
                    else:
                        pollutant_value =  ncFile[vertical_column_group].variables[total_column_name][0][lat_scanline_count][
                            lat_ground_pixel_count]
                    if (pollutant_value != "--"):
                        # pollutant_value = pollutant_value * 6.022141e19
                        # #col_air=surface_pressure*avogadro/(mass_dry_air*gravity)
                        # col_air = surface_pressure * assumed_number
                        # #co_column/air_column/1e9 will give you the CO concentration in ppb.
                        #
                        # value_converted = pollutant_value/col_air/1e9
                        pollutant_value = pollutant_value
                        lat_approximated_value = float('{:.4f}'.format(np.float32('{:.4f}'.format(
                            ncFile["PRODUCT"].variables['latitude'][0][lat_scanline_count][
                                lat_ground_pixel_count])).item(
                            0)))
                        lon_approximated_value = float('{:.4f}'.format(np.float32('{:.4f}'.format(
                            ncFile["PRODUCT"].variables['longitude'][0][lat_scanline_count][
                                lat_ground_pixel_count])).item(0)))

                        ntcdfValueArray.append(
                            {
                            "time": {"instant": str(monitoring_time)},
                            "surface_pressure":{"value": str(surface_pressure), "uom": str(uom_from_file_pressure)},
                            "Longitude": {"value": lon_approximated_value, "uom": str(uom_from_file_long)},
                            "Latitude": {"value": lat_approximated_value, "uom": str(uom_from_file_lat)},
                            "uom": str(uom_from_file), "value": str(pollutant_value)})

    pollutantValues = {pollutant_name: ntcdfValueArray}
    outfile = open(parsed_nc_file, 'w')
    outfile.write(json.dumps(OrderedDict(pollutantValues), indent=4, sort_keys=True))
if __name__ == '__main__':
   read_pollution_db()

