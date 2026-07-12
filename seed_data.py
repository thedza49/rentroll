import os
import glob
from datetime import datetime
from app import app
from importer import import_rent_roll

def seed():
    with app.app_context():
        # Get all CSV files in docs/
        csv_files = glob.glob("docs/*.csv")

        # Sort them by filename which roughly corresponds to date
        csv_files.sort()

        for csv_path in csv_files:
            filename = os.path.basename(csv_path)
            # Try to extract date from filename
            # formats: rent_roll_YYYY_MM_DD.csv or rent_roll-YYYYMMDD.csv

            date_str = None
            if "rent_roll_" in filename:
                date_str = filename.replace("rent_roll_", "").replace(".csv", "")
                date_obj = datetime.strptime(date_str, "%Y_%m_%d").date()
            elif "rent_roll-" in filename:
                date_str = filename.replace("rent_roll-", "").replace(".csv", "")
                date_obj = datetime.strptime(date_str, "%Y%m%d").date()
            else:
                print(f"Skipping {filename}, unknown format")
                continue

            print(f"Importing {filename} for date {date_obj}")
            import_rent_roll(csv_path, date_obj)

if __name__ == "__main__":
    seed()
