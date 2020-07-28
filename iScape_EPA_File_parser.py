# Dublin City Council File produced by EPA used by iScape porject as a reference
# Parsing the file and splitting it into 3 standardised json files for NO2, CO and SO2
# Transform date format to ISO 8601
# The Frequency of the data is every 15 minutes

import csv
import json
import pandas as pd
def display():
    column_names = []
    column_uom = []
    sck = []
    count = 0
    number_of_columns = 0
    file_path = "2019-03_EXT_UCD_URBAN_BACKGROUND_API_CITY_COUNCIL_REF.csv"
    file_path_OGC_CO = "CO_EPA_REF.json"
    file_path_OGC_NO2 = "NO2_EPA_REF.json"
    file_path_OGC_SO2 = "SO2_EPA_REF.json"
    CO_file = open(file_path_OGC_CO, "w")
    SO2_file = open(file_path_OGC_SO2, "w")
    NO2_file = open(file_path_OGC_NO2, "w")
    column_title = pd.read_csv(file_path, nrows=1).columns.tolist()
    column_count = len(column_title)
    column_count = len(column_title)
    column_names.append("time")
    column_uom.append("ISO 8601")
    co_file_data = []
    no2_file_data = []
    so2_file_data = []
    for uom_count in range (1 ,column_count):
        uom_start_indx = str(column_title[uom_count]).find('_')
        uom_end_indx = (str(column_title[uom_count]).__len__())
        pos_uom = uom_start_indx + 1
        if(str(column_title[uom_count][pos_uom])!= 'u'):
            column_names.append((column_title[uom_count][0:uom_start_indx]))
            column_uom.append((column_title[uom_count][(uom_start_indx + 1):uom_end_indx]))
            number_of_columns = number_of_columns + 1
    with open(file_path,'r') as csv_file:
        number_of_columns = number_of_columns + 1
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            if count == 0:
                count = count + 1
            else:
                json_file_data = []
                for data_count in range(0,  number_of_columns):
                    if(data_count == 0 ):
                        parsedDate = row[0].replace(" ", 'T')
                        time = parsedDate + 'Z'
                    else:
                        value = row[data_count] ## will only take converted values with ugm3 as EPA is with this unit
                        if (("CO") in str(column_names[data_count])):
                            co_file_data.append({"value": value, "uom": column_uom[data_count], column_names[0]: {"instant": time}})
                        elif (("NO2") in str(column_names[data_count])):
                            no2_file_data.append({"value": value, "uom": column_uom[data_count], column_names[0]: {"instant": time}})
                        elif (("SO2") in str(column_names[data_count])):
                            so2_file_data.append(
                                {"value": value,"uom": column_uom[data_count], column_names[0]: {"instant": time}})

    CO_DATA = {"CO": co_file_data}
    NO2_DATA = {"NO2": no2_file_data}
    SO2_DATA = {"SO2": so2_file_data}
    CO_file.write(str(json.dumps(CO_DATA, sort_keys=True, indent=4, ensure_ascii=False)))
    NO2_file.write(str(json.dumps(NO2_DATA, sort_keys=True, indent=4, ensure_ascii=False)))
    SO2_file.write(str(json.dumps(SO2_DATA, sort_keys=True, indent=4, ensure_ascii=False)))
    return

if __name__ == '__main__':
    display()