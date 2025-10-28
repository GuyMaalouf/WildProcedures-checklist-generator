# Drone Operations Checklist Generator

A standalone Python tool for generating customized drone operation checklists and procedure manuals in PDF format.

## Features

- Generate compact A5 checklists for field use
- Generate detailed A4 procedure manuals
- Filter procedures based on:
  - Operation type (VLOS, BVLOS with/without observer, Night operations)
  - Drone platform (DJI, Ebee X, UoB Glider, Papa Smurf, CoDrone, Parrot Anafi)
  - Number of drones (Single, Multiple, Swarm)
- Professional PDF formatting with custom fonts and branding

## Requirements

- Python 3.6 or higher
- fpdf library

## Installation

1. Install the required Python package:
```bash
pip install fpdf
```

## Usage

### Basic Usage

Generate checklists with default settings (VLOS, DJI, Single drone):
```bash
python generate_checklist.py
```

### Custom Configuration

Specify operation parameters:
```bash
python generate_checklist.py --operation BVLOS_NO_VO --drone EBEE --count MULTIPLE
```

Short form:
```bash
python generate_checklist.py -o NIGHT_VLOS -d PARROT -c SINGLE
```

### List Available Options

View all available options:
```bash
python generate_checklist.py --list-options
```

## Options

### Operation Types
- `VLOS` - VLOS
- `BVLOS_NO_VO` - BVLOS 1km (No Observer)
- `BVLOS_VO` - BVLOS 2km (Observer)
- `NIGHT_VLOS` - Night VLOS
- `NIGHT_BVLOS` - Night BVLOS

### Drone Platforms
- `DJI` - DJI
- `EBEE` - Ebee X
- `UOB_GLIDER` - UoB Glider
- `SMURF` - Papa Smurf
- `CODRONE` - CoDrone
- `PARROT` - Parrot Anafi

### Number of Drones
- `SINGLE` - Single Drone
- `MULTIPLE` - Multiple Drones
- `SWARM` - Swarm of Drones

## Output

The script generates PDFs in organized folders within the `output/` directory:

### Current Generation
Each time you run the script, it creates a new folder named:
```
{OPERATION_TYPE}_{DRONE_PLATFORM}_{NUMBER_OF_DRONES}_{TIMESTAMP}/
```

This folder contains two PDF files:
- `checklist.pdf` - Compact A5 field checklist with checkboxes
- `procedures.pdf` - Detailed A4 procedure manual with descriptions

Example:
```
output/
└── VLOS_DJI_SINGLE_20251028_143012/
    ├── checklist.pdf
    └── procedures.pdf
```

### Archive
When you generate new PDFs, the previous generation folder is automatically moved to `output/archive/`. This keeps your output directory clean while preserving all historical generations.

Example after multiple generations:
```
output/
├── NIGHT_VLOS_PARROT_MULTIPLE_20251028_143033/  ← Latest
│   ├── checklist.pdf
│   └── procedures.pdf
└── archive/
    ├── VLOS_DJI_SINGLE_20251028_143012/
    ├── BVLOS_NO_VO_EBEE_SWARM_20251028_141317/
    └── ...
```

## Directory Structure

```
.
├── generate_checklist.py    # Main script
├── interactive_generator.py  # Interactive mode script
├── README.md                 # This file
├── QUICKSTART.md             # Quick start guide
├── LICENSE                   # License information
├── requirements.txt          # Python dependencies
├── data/
│   ├── constants.json        # Configuration for operation types, drones, etc.
│   └── json/                 # Checklist data files
│       ├── 00_operation_planning.json
│       ├── 01_pre_operation.json
│       ├── 02_packing.json
│       ├── 03_first_flight.json
│       ├── 04_pre_flight.json
│       ├── 05_in_flight.json
│       ├── 06_post_flight.json
│       ├── 07_post_operation.json
│       ├── 08_contingency_procedures.json
│       └── 09_emergency_procedures.json
├── fonts/                    # Custom fonts
│   ├── Open_Sans/
│   └── Montserrat/
├── media/                    # Logo and images
│   └── WD_logo.png
└── output/                   # Generated PDFs
    ├── {CONFIG}_{TIMESTAMP}/ # Latest generation folder
    │   ├── checklist.pdf
    │   └── procedures.pdf
    └── archive/              # Previous generations
        ├── {CONFIG}_{TIMESTAMP}/
        └── ...
```

## Customization

### Customizing Operation Types, Drone Platforms, or Drone Counts

Edit `data/constants.json` to modify the available options. The file structure is:

```json
{
    "operation_types": [
        ["CODE", "Display Name"],
        ...
    ],
    "drone_platforms": [
        ["CODE", "Display Name"],
        ...
    ],
    "number_of_drones": [
        ["CODE", "Display Name"],
        ...
    ]
}
```

### Adding New Procedures

Edit the JSON files in `data/json/` to add or modify procedures. Each procedure should follow this structure:

```json
{
    "checklist_entry": "Brief checklist item",
    "procedure_description": "Detailed procedure description",
    "operation_types": ["VLOS", "BVLOS", "EVLOS"] or ["ALL"],
    "drone_platforms": ["DJI", "AUTEL", "OTHER"] or ["ALL"],
    "number_of_drones": ["SINGLE", "MULTIPLE"] or ["ALL"]
}
```

### Changing Branding

Replace `media/WD_logo.png` with your own logo (recommended size: 28mm width at 72 DPI).

## License

This tool is provided as-is for drone operation planning and safety purposes.

## Support

For issues or questions, please refer to the JSON data files for procedure content or the script comments for technical details.
