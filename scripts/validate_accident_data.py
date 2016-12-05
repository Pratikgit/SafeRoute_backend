import csv
import sys

def validate_csv(input_csv_file, output_csv_file):
    f1 = open(input_csv_file, "rb")
    f2 = open(output_csv_file, "wb")
    reader = csv.reader(f1)
    writer = csv.writer(f2, delimiter=',')
    writer.writerow(["CC Number", "Date", "Time", "Accident Type", "Latitude", "Longitude"])
    for row in reader:
        if row[4] and row[4]!='Location 1':
            lat_string = float(row[4].split('(')[1].split(',')[0])
            long_string = float(row[4].split(", ")[1].split(")")[0])
            print lat_string, long_string
            crime_row = [row[0], row[1], row[2], row[3], lat_string, long_string]
            writer.writerow(crime_row)

    f1.close()
    f2.close()

if __name__ == "__main__":
    print sys.argv
    validate_csv(sys.argv[1], sys.argv[2])
    

    

