# 📁 AutoAnalytiX Data Directory

Place your telemetry data files in this directory for analysis.

## 📋 Required Files

### 🚛 telemetry_1.csv (Wide Format)
Primary telemetry stream with columns in wide format.

```csv
vehicle_id,timestamp,speed,odometer,fuel_level
VEH001,2024-01-01 08:00:00,0,50000,85.5
VEH001,2024-01-01 08:05:00,35,50002,85.2
VEH002,2024-01-01 08:00:00,15,75000,62.3
```

### 📊 telemetry_2.csv (Long Format)
Secondary telemetry stream with parameter-value pairs.

```csv
vehicle_id,timestamp,name,val
VEH001,2024-01-01 08:00:00,speed,0
VEH001,2024-01-01 08:00:00,odometer,50000
VEH001,2024-01-01 08:00:00,fuel_level,85.5
VEH002,2024-01-01 08:00:00,speed,15
```

### 🚗 vehicle_data.csv (Vehicle Metadata)
Vehicle specifications for analysis calculations.

```csv
id,tank_capacity,rated_mpg
VEH001,50,8.5
VEH002,60,7.2
VEH003,55,9.1
```

## 📝 Data Requirements

### Mandatory Columns
- **vehicle_id/id**: Unique vehicle identifier
- **timestamp**: Date/time in any standard format
- **speed**: Vehicle speed (mph)
- **odometer**: Odometer reading (miles)
- **fuel_level**: Fuel level percentage (0-100)
- **tank_capacity**: Tank size in gallons
- **rated_mpg**: Manufacturer's rated MPG

### Data Quality Notes
- [OK] Missing values are handled automatically
- [OK] Timestamps are parsed flexibly
- [OK] Duplicate records are removed during processing
- ⚠️ Invalid fuel levels (<0% or >100%) will be flagged and cleaned

## 🚀 Quick Start

1. **Copy your CSV files** to this directory
2. **Ensure file names match** exactly: `telemetry_1.csv`, `telemetry_2.csv`, `vehicle_data.csv`
3. **Run analysis**: `python setup.py` from project root

## 🔍 Alternative Data Sources

If CSV files are not found here, AutoAnalytiX will automatically look for:
- Google Colab mounted drive at `/content/drive/MyDrive/PS/AutoAnalytiX/Telemetry Data/`

---

📋 **Need help?** Check the main README.md for complete documentation and troubleshooting.