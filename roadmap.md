# Roadmap

## Version 1.0 (MVP)

### Dashboard

- [x] Portfolio summary (total rent row on Unit Inventory table)
- [x] Unit Inventory & Rent Health
- [x] Recent Activity feed
- [x] Financial Trends chart (total rent + occupancy %, dual-axis)
- [x] Historical snapshot selector

### Import

- [x] CSV upload
- [x] Snapshot date picker
- [x] Duplicate snapshot replacement

### Storage

- [x] SQLite database
- [x] Permanent history

---

## Version 1.1

### Lease Management

- [ ] Lease expiration calendar
- [ ] Upcoming renewals
- [ ] Expiring leases dashboard

### Additional Metrics

- [ ] Vacancy percentage
- [ ] Average rent
- [ ] Occupied units
- [ ] Vacant units

---

## Version 1.2

### Property Pages

- [ ] Property-level dashboards
- [ ] Property trends
- [ ] Unit history

### Reporting

- [ ] Export to PDF
- [ ] Export to CSV

---

## Version 1.3

### Google Drive Integration

- [ ] Automatically monitor a Google Drive folder and import new rent roll files

Workflow:

Property Manager Export

↓

Google Drive Folder

↓

Rent Roll Portal

↓

Automatic Import

No manual uploads required.

---

## Version 1.4

### Notifications

- [ ] Lease expiration reminders
- [ ] Vacancy alerts
- [ ] Rent increase reminders

---

## Version 1.5

### Analytics

- [ ] Rent growth trends
- [ ] Vacancy trends
- [ ] Property comparisons

---

## Data Cleanup

- [x] Rename units at 752 N 26th St. (was "1", "2", "3", "4") to match the
      "[street number] [unit]" naming convention used everywhere else.
      Normalized on import going forward (`importer.py`); existing history
      updated via `migrate_26th_st_units.py`.

---

## Future Ideas

- [ ] Expense tracking
- [ ] Cash flow dashboard
- [ ] Security deposit tracking
- [ ] Cap rate metrics
- [ ] Tenant history
- [ ] Notes by property
- [ ] Mobile-friendly layout improvements
- [ ] Authentication
- [ ] Multi-user support
- [ ] Email reports
- [ ] Backup and restore tools
