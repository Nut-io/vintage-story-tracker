import requests
import re
import csv
import os
from datetime import datetime, timezone, timedelta, date

CSV_PATH = 'data/data.csv'

def get_date(profile_id):
    url = f'https://www.vintagestory.at/profile/{profile_id}-x/'
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
    match = re.search(r"datetime='([^']+)'", r.text)
    if match:
        dt = datetime.fromisoformat(match.group(1).replace('Z', '+00:00'))
        return dt
    return None

def find_first_id_on(target_date, low=200000, high=2000000):
    while low < high - 1:
        mid      = (low + high) // 2
        dt       = get_date(mid)
        if dt is None:
            dt = get_date(mid + 1)
        if dt is None:
            dt = get_date(mid - 1)
        date_val = dt.date() if dt else None
        if date_val and date_val < target_date:
            low = mid
        else:
            high = mid
    return high

def get_monthly_dates(start_year, start_month, end_date):
    dates   = []
    current = date(start_year, start_month, 1)
    while current <= end_date:
        dates.append(current)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return dates

# Create CSV with header if it doesn't exist
os.makedirs('data', exist_ok=True)
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, 'w', newline='') as f:
        csv.writer(f).writerow(['date', 'total_accounts', 'new_since_last_month'])

# Load already scraped dates so we don't re-scrape them
existing_dates = set()
with open(CSV_PATH, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        existing_dates.add(row['date'])

today        = date.today()
target_dates = get_monthly_dates(2024, 1, today)

# Only scrape dates we don't already have
missing_dates = [d for d in target_dates if str(d) not in existing_dates]
print(f'{len(missing_dates)} new months to scrape')

if missing_dates:
    # Include the previous known date for subtraction
    all_dates    = sorted(set(target_dates))
    boundary_ids = {}
    for d in all_dates:
        print(f'  Finding ID for {d}...')
        boundary_ids[d] = find_first_id_on(d)
        print(f'  → {boundary_ids[d]:,}')

    with open(CSV_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        for i, d in enumerate(all_dates):
            if str(d) in existing_dates:
                continue
            total          = boundary_ids[d]
            new_since_last = 0 if i == 0 else total - boundary_ids[all_dates[i - 1]]
            writer.writerow([d, total, new_since_last])
            print(f'  {d} → total: {total:,} | new: {new_since_last:,}')

print('Done!')
