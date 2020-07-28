# This file is the log for the in-situ sensors placed for iScape project
# Smart Citizen Kit was placed in UCD
# The file is split into three standardized json files for O3, NO2 and O3
# Date format is transformed to ISO-8601 format
# Value of pollutant is extracted depending on recommendation from iScape Forum
import csv
import json
import pandas as pd
def display():
    column_names = []
    column_uom = []
    count = 0
    time = ""
    file_path = "5262_PROCESSED.csv"
    file_path_OGC_CO = "CO.json"
    file_path_OGC_O3 = "O3.json"
    file_path_OGC_NO2 = "NO2.json"
    CO_file = open(file_path_OGC_CO, "w")
    O3_file = open(file_path_OGC_O3, "w")
    NO2_file = open(file_path_OGC_NO2, "w")
    column_title = pd.read_csv(file_path, nrows=1).columns.tolist()
    column_count = len(column_title)
    column_names.append("time")
    column_uom.append("ISO 8601")
    for uom_count in range (1 ,column_count):
        uom_start_indx = str(column_title[uom_count]).find('_')
        uom_end_indx = (str(column_title[uom_count]).__len__())
        column_names.append((column_title[uom_count][0:uom_start_indx]))
    with open(file_path,'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        co_file_data = []
        no2_file_data = []
        o3_file_data = []
        for row in reader:
            if count == 0:
                count = 1
            else:
                for data_count in range(0, column_count):
                    if(data_count == 0 ):
                        parsedDate = row[0].replace(" ", 'T')
                        time = parsedDate.replace("+00:00", 'Z')
                    else:       # Value of pollutant is extracted depending on recommendation from iScape Forum
                        if ((("OVL_0-30-50") in str(column_title[data_count])) and not (
                                    ("FILTER") in str(column_title[data_count])) and not (
                                    ("GB") in str(column_title[data_count]))):
                            value = row[data_count]
                                # json_file_data.append(
                                #     {column_names[data_count]: {"value": value, "uom": column_uom[data_count]}})
                            if(("CO") in str(column_title[data_count])):
                                co_file_data.append({"value": value, "uom": "ppm",column_names[0]: {"instant": time}})
                            elif(("NO2") in str(column_title[data_count])):
                                no2_file_data.append({"value": value, "uom": "ppb",column_names[0]: {"instant": time}})
                            elif(("O3") in str(column_title[data_count])):
                                o3_file_data.append(
                                    {"value": value, "uom": "ppb",column_names[0]: {"instant": time}})
    CO_DATA = {"CO":co_file_data}
    NO2_DATA = {"NO2":no2_file_data}
    O3_DATA = {"O3": o3_file_data}
    CO_file.write(str(json.dumps(CO_DATA, sort_keys=True, indent=4, ensure_ascii=False)))
    NO2_file.write(str(json.dumps(NO2_DATA, sort_keys=True, indent=4, ensure_ascii=False)))
    O3_file.write(str(json.dumps(O3_DATA, sort_keys=True, indent=4, ensure_ascii=False)))
    return

if __name__ == '__main__':
    display()