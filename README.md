# Marwan Management CRM - Food & Beverage

A professional desktop CRM application for restaurant management built with PyQt6. Manage products, track waste, and monitor assets all in one place.

## Features

- **Dashboard**: Overview with key metrics and visual charts
- **Products Management**: Full CRUD operations for inventory items
- **Waste Tracking**: Monitor waste with detailed reporting and charts
- **Assets Management**: Track restaurant equipment and assets
- **Search & Filter**: Quick search across all modules
- **Export**: Export data to CSV or Excel formats
- **Automatic Updates**: Built-in update system via GitHub releases

## Download

### Latest Release

Download the latest release from the [Releases](https://github.com/cowebsLB/marwan-managment-CRM-FnB/releases) page.

**System Requirements:**
- Windows 10 or later
- No additional software required (all dependencies included)

**Installation:**
1. Download `Marwan_CRM_vX.X.X.zip` from the releases page
2. Extract all files to a folder of your choice
3. Double-click `Marwan_CRM.exe` to run

**Note:** The updater script is embedded in the executable and will be automatically extracted when needed for updates.

## Development Setup

### Requirements

- Python 3.8 or higher
- PyQt6
- matplotlib
- pandas
- openpyxl
- requests
- psutil

### Installation

1. Clone this repository:
```bash
git clone https://github.com/cowebsLB/marwan-managment-CRM-FnB.git
cd marwan-managment-CRM-FnB
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

Run the main application:
```bash
python main.py
```

## Building Executable

To create a standalone Windows executable with optimizations:

```bash
pip install pyinstaller
python -m PyInstaller Marwan_CRM.spec --clean
```

Or use the optimized build script:
```bash
build_optimized.bat
```

The executable will be created in the `dist` folder.

### Size Optimizations

The build includes several optimizations to reduce executable size:
- Excludes unused modules (tkinter, testing frameworks, etc.)
- Strips debug symbols
- Python bytecode optimization
- UPX compression (if available - can reduce size by 20-40%)

**Expected size:** ~100-120 MB (vs ~150 MB without optimizations)

For more details, see [BUILD_OPTIMIZATION.md](BUILD_OPTIMIZATION.md).

**Note:** The `updater_script.py` is automatically embedded in the executable via the spec file, so no separate file is needed.

## Database

The application uses SQLite3 for data storage. The database file (`restaurant_crm.db`) will be automatically created in the same directory as the executable on first run.

The database includes sample data for immediate testing.

## Automatic Updates

The application includes an automatic update system that checks for new releases on GitHub.

- Click the "🔄 Check for Updates" button in the top bar
- The system will check for new versions and notify you if an update is available
- Updates can be downloaded and installed automatically

**Note:** The updater script is embedded in the executable and will be automatically extracted when needed. No separate files required.

## Project Structure

```
restaurant_crm/
├── main.py                 # Main application entry point
├── database/
│   └── db.py              # Database operations and initialization
├── ui/
│   ├── dashboard.py       # Dashboard page
│   ├── products.py        # Products management page
│   ├── waste.py           # Waste tracking page
│   └── assets.py          # Assets management page
├── utils/
│   ├── charts.py          # Chart generation utilities
│   └── helpers.py         # Helper functions and utilities
└── assets/
    ├── icons/             # Application icons
    └── styles/            # Style sheets
```

## Usage

### Products
- Add, edit, and delete products
- Track quantity and unit prices
- Organize by categories
- Search and filter products

### Waste
- Record waste entries with reasons
- View waste statistics by reason
- Track waste over time
- Export waste reports

### Assets
- Manage restaurant equipment and assets
- Track purchase dates and values
- Monitor asset conditions
- Calculate total asset value

## License

This project is for internal use by Marwan Management.

