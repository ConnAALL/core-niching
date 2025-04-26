#!/usr/bin/env python3
"""
clean_current_csvs.py

1. Delete any CSV named CA_Qn_m.csv with m > 16
2. For the rest:
   - Read with csv.reader (so quoted commas stay inside a single field)
   - Take only the last row
   - Zero out the first three fields
   - Set the 4th field to "None"
   - Zero out the last field
   - Write the fixed header, then that single row
"""

import csv
import re
from pathlib import Path

def clean():
    cwd    = Path('.')
    header = ['Kills', 'Self Deaths', 'Total Deaths',
              'Cause of Death', 'Binary Chromosome', 'Time Elapsed']

    pattern = re.compile(r'^CA_Q\d+_(\d+)\.csv$', re.IGNORECASE)

    for csv_path in cwd.glob("*.csv"):
        # 1. Delete any CA_Qn_m with m>16
        m = pattern.match(csv_path.name)
        if m:
            if int(m.group(1)) > 16:
                csv_path.unlink()
                print(f"Deleted {csv_path.name} (m={m.group(1)} > 16)")
                continue

        # 2. Read all rows properly
        with csv_path.open('r', newline='', encoding='utf-8') as infile:
            rows = list(csv.reader(infile))

        if not rows:
            # skip empty files
            continue

        # 3. Grab the last row
        last_row = rows[-1]

        # 4a. Zero out the first three fields
        for i in range(min(3, len(last_row))):
            last_row[i] = '0'

        # 4b. Set the 4th field to "None"
        if len(last_row) > 3:
            last_row[3] = 'None'

        # 4c. Zero out the last field
        if last_row:
            last_row[-1] = '0'

        # 5. Overwrite file with header + modified row
        with csv_path.open('w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header)
            writer.writerow(last_row)

        print(
            f"Cleaned {csv_path.name}: "
            f"zeroed first 3 fields, set 4th to None, zeroed last field"
        )

if __name__ == "__main__":
    clean()
