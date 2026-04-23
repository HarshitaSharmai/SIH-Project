import csv

INPUT_CSV = "data/namaste.csv"
OUTPUT_CSV = "data/namaste_clean.csv"

header = None
rows = []

with open(INPUT_CSV, newline='', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    for row in reader:
        # Skip empty lines
        if not any(cell.strip() for cell in row):
            continue
        # Detect header
        if row and row[0].strip() == "NAMASTE_Code":
            if not header:
                header = row
            continue  # skip duplicate headers
        # Skip rows that don't have all columns
        if len(row) != 5:
            continue
        rows.append(row)

with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(header)
    writer.writerows(rows)

print(f"Cleaned CSV written to {OUTPUT_CSV}")
