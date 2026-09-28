"""Import the GeoNames US postal archive downloaded by the caller; no runtime network."""
import csv
import sys
import zipfile
from pathlib import Path

STATES = set('AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY'.split())
root = Path(__file__).resolve().parents[1]
rows = {}
with zipfile.ZipFile(sys.argv[1]) as archive:
    for line in archive.read('US.txt').decode().splitlines():
        fields = line.split('\t')
        if fields[4] in STATES and fields[9] and fields[10]:
            rows.setdefault(fields[1], [fields[1], fields[2], fields[4], fields[9], fields[10]])
with (root / 'backend/data/us_zips.csv').open('w') as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(['zip_code', 'city', 'state', 'latitude', 'longitude'])
    writer.writerows(rows[key] for key in sorted(rows))
print(f'Imported {len(rows)} ZIP codes in {len({row[2] for row in rows.values()})} states/DC.')
