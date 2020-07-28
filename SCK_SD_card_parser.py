
# Reading all data saved in SD-Card
# Saving data in main attribute (field)
# Every Variable has value and unit of measurement
import csv
import json

def display():
    column_SD_title = []
    column_SD_uom = []
    sck = []
    column_count = 0
    count = 0
    data = ""
    sd_card_file_path = "from SD card/19-07-15.CSV"
    sd_card_file_path_ogc = "from SD card/19-07-15.json"
    sck_sd_file = open(sd_card_file_path_ogc, "w")
    with open(sd_card_file_path) as csvfile_sd:
        csvfile_sd_begin = csvfile_sd
        for line in csvfile_sd:
            column_count = line.count(',') + 1
            break

        read_csv_sd = csv.reader(csvfile_sd_begin, delimiter=',')
        for row in read_csv_sd:
            if count == 0:  # first row has unit of measurement
                for uom_count in range(0, column_count):
                    column_SD_uom.append(row[uom_count])
                count = count + 1
            elif count == 1:  # Second row has titles of measurements (Temperature, Humidity , etc..)
                for col_count in range(0, column_count):
                    column_SD_title.append(row[col_count])

                count = count + 1
            elif count == 2: # Skip rows till data is written
                count = count + 1
            elif count == 3:
                count = count + 1
            else:
                json_file_data = []
                ###### Save Data and unit of Measurements ##########
                for data_count in range(0, column_count):
                    if data_count == 0:
                        json_file_data.append(
                            {column_SD_title[data_count]: {"instant": row[data_count], "uom": column_SD_uom[data_count]}})
                    else:
                        json_file_data.append(
                        {column_SD_title[data_count]: {"value": row[data_count], "uom": column_SD_uom[data_count]}})

                sck.append({"field": json_file_data})
    data = {"SCK": sck}
    sck_sd_file.write(json.dumps(data, indent=4)) ## Dump data in JSON file

    return

if __name__ == '__main__':
    display()



