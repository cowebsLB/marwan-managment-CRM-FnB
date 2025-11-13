# Marwan Management CRM - Food & Beverage

A professional desktop CRM application for restaurant management built with PyQt6. Manage products, track waste, and monitor assets all in one place.

## Features

- **Dashboard**: Overview with key metrics and visual charts
- **Products Management**: Full CRUD operations for inventory items
- **Waste Tracking**: Monitor waste with detailed reporting and charts
- **Assets Management**: Track restaurant equipment and assets
- **Search & Filter**: Quick search across all modules
- **Export**: Export data to CSV or Excel formats

## Requirements

- Python 3.8 or higher
- PyQt6
- matplotlib
- pandas
- openpyxl

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Run the main application:
```bash
python main.py
```

## Building Executable

To create a standalone Windows executable:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "Marwan_CRM" main.py
```

The executable will be created in the `dist` folder.

## Database

The application uses SQLite3 for data storage. The database file (`restaurant_crm.db`) will be automatically created in the project root directory on first run.

The database includes sample data for immediate testing.

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

