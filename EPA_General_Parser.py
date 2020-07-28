# EPA datasets differ in format
# The parser reads the Dataset and depending on it, it works generate a standardised JSON file
import csv
import json
import re
import datetime
import glob
import pandas as pd


def display():
    pollutant_NO = ""
    pollutant_name = ""
    pollutant_NO2 = ""


    # reading the csv file
    for pollutant_file in glob.glob("EPA Monitoring Data/*.csv"):


       with open( pollutant_file) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            pollutant_array = []
            NOArray = []
            NO2Array = []
            count = 0
            polluatnt_uom = ""
            uom_NO = ""
            uom_NO2 = ""
            parsed_pollutant = ""
            parse_NO = ""
            parse_NO2 = ""

            year = ""
            for row in readCSV:
                if count == 0:
                    pollutant_name = row[2]
                    if pollutant_name == 'ug m-3':
                        pollutant_name = "SO2"
                    if("NO" in pollutant_name):
                        pollutant_NO = row[3]
                        pollutant_NO2 = row[4]
                        count = 1
                    if("ug" in pollutant_name):  # case in SO2 datasets
                        polluatnt_uom = row[2]
                        pollutant_name = "SO2"
                        count = 2
                    else:
                        count = 1
                elif count == 1:
                    polluatnt_uom = row[2]
                    if("NO" in pollutant_name):  # case in NOx datasets
                        uom_NO = row[3]
                        uom_NO2 = row[4]
                    count = 2
                else:
                    date = (row[0])
                    check = re.match('(\d{1,2})/(\d{1,2})/(\d{4})', date)
                    if check:
                        month = int(check.group(1))
                        day = int(check.group(2))
                        year = int(check.group(3))
                        hour = (int(row[1]) - 1)  # decrement hours as in EPA file 1-24 and OGC 0-23 WRONG CHANGE TO 24 ==23
                        tempDate = str(datetime.datetime(year, month, day, hour))
                        # apply OGC standards on the data format
                        parsedDate = tempDate.replace(" ", 'T')  # replace the space with (T)
                        parsedDateWithZ = parsedDate.__add__('Z')
                        pollutant_array.append({"time": {"instant": parsedDateWithZ}, "value": row[2], "uom": polluatnt_uom})
                        if "NO" in pollutant_name:
                            NOArray.append({"time": {"instant": parsedDateWithZ}, "value": row[3], "uom": uom_NO})
                            NO2Array.append({"time": {"instant": parsedDateWithZ}, "value": row[4], "uom": uom_NO2})

            parsed_pollutant = {pollutant_name:pollutant_array}
            pollutant_file_path = "EPA Monitoring Data/"+pollutant_name+"_2018.json" #create json file
            pollutant_file = open(pollutant_file_path, "w")
            # writing parsed data on it
            pollutant_file.write(json.dumps(parsed_pollutant, indent=4))
            if "NO" in pollutant_name:  # if input file is NOx then it will be split to 3 files : NOx, NO and NO2
                parse_NO = {pollutant_NO: NOArray}
                parse_NO2 = {pollutant_NO2: NO2Array}
                NO_file_path = "EPA Monitoring Data/NO_2018.json"
                NO2_file_path = "EPA Monitoring Data/NO2_2018.json"
                NO_file = open(NO_file_path, "w")
                NO2_file = open(NO2_file_path, "w")
                NO_file.write(json.dumps(parse_NO, indent=4))
                NO2_file.write(json.dumps(parse_NO2, indent=4))


if __name__ == '__main__':
       display()
