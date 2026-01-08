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

### Download FIT files

Download FIT files for the retrieved activities:
```bash
stryd -g 7 -f           # Download FIT files for activities from last 7 days
stryd -g 30 --fit       # Download FIT files for activities from last 30 days
stryd -d 20260108 -f    # Download FIT files for activities on a specific date
```

Specify a custom output directory:
```bash
stryd -g 7 -f -o my_fit_files/    # Save to custom directory
```

## Project Structure

```
strydcmd/
├── strydcmd/           # Main package
│   ├── __init__.py     # Package initialization
│   ├── stryd_api.py    # Stryd API client
│   └── main.py         # CLI entry point
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
- ✅ Display activity details (distance, pace, power, heart rate)
- ✅ Download FIT files for activities

## Roadmap

- 🔜 Power data analysis
- 🔜 Training zones calculation
- 🔜 Tag filtering
- 🔜 Export to CSV/JSON

## Stryd API

The tool uses the following Stryd API endpoints:
- `POST /b/email/signin` - Authentication
- `GET /b/api/v1/users/calendar` - Retrieve activities
- `GET /b/api/v1/activities/{id}/fit` - Download FIT file

## Development

To contribute or modify the code:

1. Main code is in `strydcmd/stryd_api.py`
2. CLI entry point is in `strydcmd/main.py`
3. Tests can be run with the `stryd` command

## License

To be defined
