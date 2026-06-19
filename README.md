# Rent Roll Portal

A lightweight self-hosted dashboard for tracking rental portfolio performance over time.

Rent Roll Portal is designed to run on a Raspberry Pi and requires minimal maintenance. Each month, upload the latest rent roll export from the property management software and the application automatically updates the dashboard while preserving historical snapshots.

## Features

* Historical rent roll snapshots
* Monthly CSV upload with snapshot date selection
* Automatic replacement of duplicate snapshot dates
* Unit Inventory & Rent Health dashboard
* Recent Activity feed
* Historical Financial Trends
* Property-level rollups
* Unit-level detail
* SQLite database (no external database required)
* Raspberry Pi friendly

## Technology

* Python
* Flask
* SQLite
* Pandas
* Bootstrap
* Chart.js

## Monthly Workflow

1. Download rent roll CSV from property manager.
2. Open Rent Roll Portal.
3. Upload the file.
4. Select the snapshot date.
5. Import.

The dashboard updates automatically and preserves all previous months.

## Repository Structure

rent-roll-portal/

```
app.py

activity.py
importer.py
models.py

database/
    rent_roll.db

uploads/

templates/
    dashboard.html
    upload.html

static/
    style.css

README.md
ROADMAP.md
requirements.txt
```

## Dashboard Components

### Portfolio Summary

Current snapshot metrics.

### Unit Inventory & Rent Health

Displays:

* Property
* Unit
* Status
* Current Rent
* Last Increase
* Next Increase Due

### Recent Activity

Tracks:

* New tenants
* Rent increases
* Vacancies
* Reoccupied units

### Financial Trends

Historical charts:

* Gross Rent
* Occupancy

Supports:

* Last 12 months
* Last 24 months

## Data Storage

SQLite stores:

### Snapshots

One record for each monthly import.

### Unit Snapshots

Historical copy of every unit for every month.

### Activities

Permanent event history generated from comparing consecutive snapshots.

## Deployment

Designed to run continuously on a Raspberry Pi.

No Docker required.

No external database required.

No cloud services required.

## License

Personal use.
