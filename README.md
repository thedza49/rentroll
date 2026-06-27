# Rent Roll Portal

A Flask-based application to manage and analyze property rent rolls.

## Features

- **Portfolio Dashboard**: Summary metrics (Potential Gross), financial trends chart, and recent activity feed.
- **CSV Import**: Upload monthly rent roll snapshots and automatically track changes.
- **Activity Tracking**: Automatically detects vacancies, reoccupancies, and rent increases between snapshots.
- **Unit Inventory**: Detailed view of unit status, rent, and upcoming increases.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```
   The application will be available at `http://localhost:5050`.

## Project Structure

- `app.py`: Main Flask application and routes.
- `models.py`: Database models for Snapshots, UnitSnapshots, and Activities.
- `importer.py`: Logic for parsing CSV files and importing snapshots.
- `activity.py`: Logic for generating activity records by comparing snapshots.
- `templates/`: HTML templates for the dashboard and upload pages.
- `static/`: CSS styles and other static assets.
