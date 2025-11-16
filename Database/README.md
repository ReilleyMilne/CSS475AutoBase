# Database Pipeline — Setup & Usage

This pipeline automates the conversion of CSV data into SQL INSERT statements and loads them into your MySQL database.

## Overview

- **DataGenerator.py** — Converts CSV files to SQL INSERT scripts
- **DataInserter.py** — Executes SQL scripts against your MySQL database
- **Run.py** — Orchestrates both steps in sequence

## Prerequisites

1. **Python 3.7+** with dependencies:

2. **MySQL server** running and accessible

3. **CSV files** If using Fabricate to generate data, put files in the `AutoBase/` directory (e.g., `Customer.csv`, `Vehicle.csv`). If using Mockaroo files will be generated automatically.

## Environment Setup

Create a `.env` file in the root of your project with the following variables:

```
DB_HOST=localhost
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
MOCKAROO_API_KEY=your_mockaroo_key_if_using_mockaroo
```

**Note:** The `MOCKAROO_API_KEY` is only required if you plan to use `fetch_all_schemas()` in DataGenerator.

## Running the Pipeline

From the `Database/Pipeline/` directory:

This will:

1. Convert all CSV files in `AutoBase/` to SQL scripts in `MockData/`
2. Execute all SQL scripts against your configured database
3. Generate authentication records for `Employee` and `Customer` tables

## File Structure

```
AutoBase/              # Input CSV files (from Fabricate.tonic.ai or generated from Mockaroo)
├── Customer.csv
├── Employee.csv
├── Vehicle.csv
└── ...

MockData/              # Generated SQL files (output)
├── MOCK_Customer_DATA.sql
├── MOCK_Employee_DATA.sql
└── ...
```

## Troubleshooting

- **"Connection refused"** — Verify MySQL is running, IP address is allowed from the hosted server, and credentials in `.env` are correct
- **"File not found"** — Ensure CSV files exist in `AutoBase/` with exact table names
- **"cURL error"** — Only occurs if using Mockaroo; requires valid API key and internet connection
