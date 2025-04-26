#!/usr/bin/env python3
"""
clean_current_csvs.py

For every .csv in the current directory:
 1. Read with csv.reader (so quoted commas stay inside a single field)
 2. Take only the last row
 3. Zero out the first four and last fields of that row
 4. Write the given header, then that single row
"""

import csv
from pathlib import Path

def clean():
    cwd = Path('.')
    header = ['Kills', 'Self Deaths', 'Total Deaths',
              'Cause of Last Death', 'Binary Chromosome', 'Time Elapsed']

    for csv_path in cwd.glob("*.csv"):
        # 1. Read in all rows properly
        with csv_path.open('r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            rows = list(reader)

        if not rows:
            # nothing to process
            continue

        # 2. Grab the last row
        last_row = rows[-1]

        # 3. Zero out the first three columns 
        for i in range(min(3, len(last_row))):
            last_row[i] = '0'

        # 3b. Set the 4th column ("Cause of Death") to "None"
        if len(last_row) > 3:
            last_row[3] = 'None'

        # 3c. Zero out the last column 
        if len(last_row) > 0:
            last_row[-1] = '0'

        # 4. Write header + modified row
        with csv_path.open('w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header)
            writer.writerow(last_row)

        print(f"Cleaned {csv_path.name}: wrote header + 1 row (zeroed first {min(3,len(last_row))} fields)")

if __name__ == "__main__":
    clean()
