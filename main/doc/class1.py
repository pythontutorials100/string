with open(INPUT_CSV, "r", encoding="utf-8") as f_in:
    reader = csv.DictReader(f_in)
    print("Detected headers:", reader.fieldnames)
    for row in reader:
        print(row)
        # break  # just to see the first row
