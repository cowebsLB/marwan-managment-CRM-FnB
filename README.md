# Marwan Management CRM - Food & Beverage

A professional desktop CRM application for restaurant management built with PyQt6. Manage products, track waste, monitor assets, and analyze data with comprehensive analytics.

## Features

- **📊 Dashboard**: Overview with key metrics and visual charts
- **📦 Products Management**: Full CRUD operations with category autofill
- **🗑️ Waste Tracking**: Monitor waste with detailed reporting and trend analysis
- **💼 Assets Management**: Track restaurant equipment and assets
- **📈 Analytics Page**: Comprehensive analytics and visualizations for all data
- **🔍 Search & Filter**: Quick search across all modules
- **📤 Export**: Export data to CSV or Excel formats
- **🔄 Automatic Updates**: Built-in update system via GitHub releases
- **✨ Modern UI**: Beautiful splash screen and smooth animations

## Download

### Latest Release

Download the latest release from the [Releases](https://github.com/cowebsLB/marwan-managment-CRM-FnB/releases) page.

**System Requirements:**
- Windows 10 or later
- No additional software required (all dependencies included)

**Installation:**
1. Download `MarwanManagementCRM.exe` from the releases page
2. Place it in a folder of your choice
3. Double-click to run

**Note:** The database (`restaurant_crm.db`) will be automatically created in the same directory as the executable on first run.

## Development Setup

### Requirements

- Python 3.8 or higher
- See `requirements.txt` for full list of dependencies

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

To create a standalone Windows executable:

### Option 1: Using the Build Script (Recommended)

**Windows:**
```bash
build.bat
```

**Or manually:**
```bash
python build_exe.py
```

### Option 2: Manual Build

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
pyinstaller --name=MarwanManagementCRM --onefile --windowed main.py
```

The executable will be created in the `dist` folder.

**Expected size:** ~50-100 MB (includes Python interpreter and all dependencies)

For detailed build instructions, see [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md).

## Database

The application uses SQLite3 for data storage. The database file (`restaurant_crm.db`) will be automatically created in the same directory as the executable on first run.

The database includes sample data for immediate testing:
- Sample products with categories
- Sample waste entries
- Sample assets

## Automatic Updates

The application includes an automatic update system that checks for new releases on GitHub.

- Click the "🔄 Check for Updates" button in the top bar
- The system will check for new versions and notify you if an update is available
- Updates can be downloaded and installed automatically

**Repository:** [cowebsLB/marwan-managment-CRM-FnB](https://github.com/cowebsLB/marwan-managment-CRM-FnB)

## Project Structure

```
marwan-managment-CRM-FnB/
├── main.py                 # Main application entry point
├── database/
│   └── db.py              # Database operations and initialization
├── ui/
│   ├── dashboard.py       # Dashboard page with metrics
│   ├── products.py        # Products management page
│   ├── waste.py           # Waste tracking page
│   ├── assets.py          # Assets management page
│   ├── analytics.py       # Analytics and reports page
│   └── splash.py          # Splash screen
├── utils/
│   ├── charts.py          # Chart generation utilities
│   ├── helpers.py         # Helper functions and utilities
│   ├── icons.py           # Icon utilities
│   ├── updater.py         # Update system core logic
│   └── updater_ui.py      # Update system UI
├── build_exe.py           # Build script for executable
├── build.bat              # Windows build batch file
└── requirements.txt       # Python dependencies
```

## Usage

### Dashboard
- View key metrics at a glance
- Visual charts for quick insights
- Summary cards for products, waste, and assets

### Products
- Add, edit, and delete products
- Track quantity and unit prices
- Organize by categories with autocomplete
- Search and filter products
- Visual highlighting for low-stock items

### Waste
- Record waste entries with reasons
- View waste statistics by reason
- Track waste trends over time
- Export waste reports

### Assets
- Manage restaurant equipment and assets
- Track purchase dates and values
- Monitor asset conditions
- Calculate total asset value

### Analytics
- Products by category (pie chart)
- Inventory value by category (bar chart)
- Waste by reason (bar chart)
- Top wasted items (bar chart)
- Waste trend over time (line chart)
- Assets by type and condition (pie charts)
- Asset value by type (bar chart)

## Version

Current Version: **1.0.0**

## License

This project is for internal use by Marwan Management.

## Contributing

This is a private project. For issues or feature requests, please contact the development team.
