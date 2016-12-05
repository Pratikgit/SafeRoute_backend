import csv
import sys

def validate_csv(input_csv_file, output_csv_file):
    f1 = open(input_csv_file, "rb")
    f2 = open(output_csv_file, "wb")
    reader = csv.reader(f1)
    writer = csv.writer(f2, delimiter=',')
    writer.writerow(["CrimeDate", "CrimeTime", "CrimeCode", "Location", "Description", "Inside/Outside", 
                    "Post", "District", "Neighborhood", "Latitude", "Longitude", "Total Incidents"])
    for row in reader:
        if row[10] and row[10]!='Location 1':
            if row[9] and (row[9] in ['Inner Harbor', 'Orangeville', 'Oldtown', 'Downtoun']):
                lat_string = float(row[10].split('(')[1].split(',')[0])
                long_string = float(row[10].split(", ")[1].split(")")[0])
                print lat_string, long_string
                crime_row = [row[0], row[1], row[2], row[3], row[4], row[5], row[7], row[8],
                            row[9], lat_string, long_string, row[11]]
                writer.writerow(crime_row)

    f1.close()
    f2.close()

if __name__ == "__main__":
    print sys.argv
    validate_csv(sys.argv[1], sys.argv[2])
    

    

