##extract data from csv file
##first row is saved in array for column names
##column name timestamp is replaced to Time
##Timestamp is converted to ISO 8601
##UOM is extracted from the column names
##All data is transfered to json file dumped as ASCII in notepad encoding is ANSI

import csv
import json
import pandas as pd


def display():
    column_wifi_title = []
    column_wifi_column_names = []
    column_wifi_uom = []
    sck = []
    column_count = 0
    count = 0
    wifi_file_path = "from WIFI/9837_1563489240741.csv"
    wifi_file_path_ogc = "from WIFI/9837_1563489240741.json"
    sck_sd_file = open(wifi_file_path_ogc, "w")
    column_wifi_title = pd.read_csv(wifi_file_path, nrows=1).columns.tolist()
    column_count = len(column_wifi_title)
    column_wifi_uom.append("ISO 8601")
    column_wifi_column_names.append("Time")
    for uom_count in range(1, column_count):
        uom_start_index = str(column_wifi_title[uom_count]).find('in ')
        uom_end_index = str(column_wifi_title[uom_count]).find('(')
        column_wifi_uom.append((column_wifi_title[uom_count][(uom_start_index+3):(uom_end_index - 1)]))
        column_wifi_column_names.append(str(column_wifi_title[uom_count][0:uom_start_index - 1]))

    with open(wifi_file_path, 'r') as csv_file_WIFI:
        reader = csv.reader(csv_file_WIFI, delimiter=',')
        for row in reader:
            if count == 0:
                count = count + 1
            else:
                json_file_data = []
                for data_count in range(0, column_count):
                    if data_count == 0:
                        parsed_date = row[0].replace(" UTC", 'Z')
                        parsed_date = parsed_date.replace(" ", 'T')  # replace the space with (T)
                        value = parsed_date
                        json_file_data.append({column_wifi_column_names[data_count]: {"instant": value,
                                                                                      "uom": column_wifi_uom[
                                                                                          data_count]}})
                    else:
                        value = row[data_count]
                        json_file_data.append({column_wifi_column_names[data_count]: {"value": value,
                                                                                      "uom": column_wifi_uom[
                                                                                          data_count]}})
                sck.append({"field": json_file_data})
    data = {"SCK": sck}
    sck_sd_file.write(str(json.dumps(data, sort_keys = True, indent = 4, ensure_ascii=False)))

    return


if __name__ == '__main__':
    display()



