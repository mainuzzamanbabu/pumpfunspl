import csv
from datetime import datetime

CSV = "launch_log.csv"
HEADERS = ['logged_at','timestamp','name','symbol','mint','metadata_uri',
           'dev_address','socials_found','top_holder_pct','score','recommend']

def init_csv():
    with open(CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, HEADERS)
        writer.writeheader()

def append_row(row):
    row2 = {'logged_at': datetime.utcnow().isoformat(), **row}
    with open(CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, HEADERS)
        writer.writerow(row2)
