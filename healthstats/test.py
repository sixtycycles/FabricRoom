from datetime import datetime
import csv

def format(row):
    
    print('\n')
    print(row[5])
    print(datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S %z"))


with open('/srv/code/media/processed/Rod/HeartRate.csv') as f:
    reader = csv.reader(f)
    #skip header data
    next(reader)
    for row in reader:

        format(row)

    print("donezo")