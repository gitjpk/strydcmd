# Stryd Command Line Tool

[🇫🇷 Version française](README.fr.md)

A command-line tool to connect to the Stryd API and retrieve your training data.

## Installation

1. Clone or create the project in your environment

2. Activate the virtual environment (already created):
```bash
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

## Configuration

1. Copy the example configuration file:
```bash
cp .env.example .env
```

2. Edit the `.env` file and add your Stryd credentials:
```
STRYD_EMAIL=your.email@example.com
STRYD_PASSWORD=your_password
```

## Usage

### Test authentication

Make sure the virtual environment is activated:
```bash
source .venv/bin/activate
stryd
```

Or use the full path without activating:
```bash
.venv/bin/stryd
```

Or directly with Python:
```bash
.venv/bin/python -m strydcmd.main
```

### Get activities

Retrieve activities from the last 30 days (default):
```bash
stryd -g
# or
stryd --get
```

Specify a custom number of days:
```bash
stryd -g 7    # Last 7 days
stryd -g 20   # Last 20 days
stryd --get 60  # Last 60 days
```

### Get activities for a specific date

Retrieve activities for a specific date (format: YYYYMMDD):
```bash
stryd -d 20260108          # Activities on January 8, 2026
stryd --date 20251225      # Activities on December 25, 2025
```

### Filter activities by tag

Filter activities by a specific tag (must be combined with -g):
```bash
stryd -g 30 -t "barcelona 26"        # Activities from last 30 days with tag "barcelona 26"
stryd -g 7 --tag "marathon training" # Activities from last 7 days with specific tag
```

If the tag is not found, the tool will display available tags from your recent activities.

### Download FIT files

Download FIT files for the retrieved activities:
```bash
stryd -g 7 -f                    # Download FIT files for activities from last 7 days
stryd -g 30 --fit                # Download FIT files for activities from last 30 days
stryd -d 20260108 -f             # Download FIT files for activities on a specific date
stryd -g 7 -t "barcelona 26" -f  # Download FIT files for activities with specific tag
```

Specify a custom output directory:
```bash
stryd -g 7 -f -o my_fit_files/    # Save to custom directory
```

### Export to CSV or JSON

Export activities to CSV or JSON format:
```bash
stryd -g 30 -e activities.csv     # Export to CSV
stryd -g 7 -e data.json           # Export to JSON
stryd -d 20260108 -e daily.csv    # Export specific date
```

### Synchronize activities to database

The `strydsync` command synchronizes detailed activity data to a local SQLite database, including all time-series data (power, heart rate, GPS, etc.):

```bash
# Sync last 30 days (default)
strydsync

# Sync custom number of days
strydsync 60     # Last 60 days
strydsync 90     # Last 90 days

# Sync specific date
strydsync -d 20260108     # January 8, 2026

# Force resynchronization (overwrite existing data)
strydsync --force         # Resync last 30 days
strydsync 90 --force      # Resync last 90 days

# Custom batch size (default: 10 activities per batch)
strydsync 30 --batch-size 5

# Custom database location
strydsync --db /path/to/my_activities.db
```

**Database Structure:**
- `activities`: Main activity metadata (87 fields)
- `zones_distribution`: Power zones distribution per activity
- `timeseries_power`: Power data over time (5 metrics)
- `timeseries_kinematics`: Speed, distance, cadence, stride length
- `timeseries_cardio`: Heart rate and RR intervals
- `timeseries_biomechanics`: Ground time, oscillation, leg spring, etc.
- `timeseries_elevation`: Elevation and grade data
- `gps_points`: GPS coordinates for mapping
- `laps`: Lap markers and workout steps

The sync process:
- ✅ Automatically skips already synced activities
- ✅ Shows progress with batch processing (10 activities by default)
- ✅ Stores complete activity details including all time-series data
- ✅ Supports force mode to update existing activities
- ✅ Creates SQLite database with indexed tables for efficient queries

**Example output:**
```
============================================================
Starting sync: 30 activities to process
Batch size: 10 activities
Force mode: OFF
============================================================

--- Batch 1/3 (activities 1-10) ---
  [1/30] → Fetching details for Morning Run (2026-01-08)...
  [1/30] ✓ Morning Run (2026-01-08) - saved
  [2/30] ✓ Evening Workout (2026-01-07) - already synced, skipping
  ...

============================================================
Sync completed!
  • New/Updated: 15
  • Skipped:     12
  • Failed:      3
  • Total in DB: 1234
============================================================
```

## Project Structure

```
strydcmd/
├── strydcmd/           # Main package
│   ├── __init__.py     # Package initialization
│   ├── stryd_api.py    # Stryd API client
│   ├── main.py         # CLI entry point for stryd command
│   ├── sync.py         # CLI entry point for strydsync command
│   └── database.py     # SQLite database management
├── .env.example        # Configuration example
├── .gitignore          # Files ignored by Git
├── pyproject.toml      # Project configuration
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Current Features

- ✅ Authentication with Stryd API
- ✅ Session token management
- ✅ User ID retrieval
- ✅ Retrieve activities for a custom time period
- ✅ Retrieve activities for a specific date
- ✅ Filter activities by tag
- ✅ Display comprehensive activity details (distance, pace, power, heart rate, zones, etc.)
- ✅ Download FIT files for activities
- ✅ Export to CSV/JSON formats with power zones
- ✅ Training zones calculation and distribution
- ✅ **Sync detailed activity data to SQLite database**
- ✅ **Store complete time-series data (power, kinematics, cardio, biomechanics, GPS)**
- ✅ **Smart sync with duplicate detection and skip**
- ✅ **Batch processing with progress tracking**

## Roadmap

- 🔜 Query and analyze database data
- 🔜 Activity visualization from database
- 🔜 Training load and trends analysis
- 🔜 Activity Map rendering (from GPS points)
- 🔜 Activity Graphs (power, HR, pace, elevation)

## Stryd API

The tool uses the following Stryd API endpoints:
- `POST /b/email/signin` - Authentication
- `GET /b/api/v1/users/calendar` - Retrieve activity summaries
- `GET /b/api/v1/activities/{id}` - Get detailed activity data (139 fields, time-series)
- `GET /b/api/v1/activities/{id}/fit` - Download FIT file

## Development

To contribute or modify the code:

1. Main code is in `strydcmd/stryd_api.py`
2. CLI entry point is in `strydcmd/main.py`
3. Tests can be run with the `stryd` command

## License

To be defined
