import csv

INPUT_CSV = "extended_defects.csv"  # or whatever your CSV file is named

with open(INPUT_CSV, "r", encoding="utf-8") as f_in:
    reader = csv.DictReader(f_in)
    print("Detected headers:", reader.fieldnames)
    for row in reader:
        print(row)
