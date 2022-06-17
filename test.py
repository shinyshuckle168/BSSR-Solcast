import numpy as np
import csv
from datetime import datetime, timedelta
from irr_forecast import day_append

forecast_dict = {'dni':['calls/20220616-203652_dni_forecasts.csv', 'calls/20220616-211815_dni_forecasts.csv'], 'dhi':['calls/20220616-203652_dhi_forecasts.csv', 'calls/20220616-211815_dhi_forecasts.csv']}

for irr, fnames in forecast_dict.items():
    day_append(fnames[0])
    fnames[0] = fnames[0][:-4] + '_appended.csv'
    day_append(fnames[1])
    fnames[1] = fnames[1][:-4] + '_appended.csv'


    with open(fnames[0], "r", newline = '') as csv_old, open(fnames[1], "r", newline='') as csv_new, open(fnames[0][:-4]+'_combined.csv', "w", newline='') as csv_comb:
        csv_old_reader = csv.reader(csv_old)
        csv_new_reader = csv.reader(csv_new)
        csv_writer = csv.writer(csv_comb)

        first = 1
        for row in csv_old_reader:
            if first:
                new_row = []
                for time in row[2:]:
                    new_time = datetime.fromisoformat(time[:-5] + '+00:00')+timedelta(days=22)
                    time_string = new_time.isoformat()[:-6]+'.0000000Z'
                    new_row.append(time_string)
                    first = 0
                new_row = row[:2] + new_row

            else:
                new_row = row

            csv_writer.writerow(new_row)

        first = 1
        second = 1
        for row in csv_new_reader:
            if first:
                first = 0
                continue
            if second:
                second =0
                continue

            new_row = row[:2] + ['', ''] + row[2:]

            csv_writer.writerow(new_row)