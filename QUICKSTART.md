# Quick Start Guide

## Installation (One-Time Setup)

```bash
pip install -r requirements.txt
```

## Usage Examples

### Interactive Mode (Easiest!)
```bash
python interactive_generator.py
```
Just follow the prompts to select your options.

### Generate default checklists (VLOS, DJI, Single Drone)
```bash
python generate_checklist.py
```

### Generate for specific configuration
```bash
# BVLOS (No Observer) with Ebee X drone, swarm of drones
python generate_checklist.py -o BVLOS_NO_VO -d EBEE -c SWARM

# Night VLOS with DJI drone, single drone
python generate_checklist.py -o NIGHT_VLOS -d DJI -c SINGLE

# BVLOS (With Observer) with Papa Smurf, multiple drones
python generate_checklist.py -o BVLOS_VO -d SMURF -c MULTIPLE
```

### View all options
```bash
python generate_checklist.py --list-options
```

### Get help
```bash
python generate_checklist.py --help
```

## Output

Generated PDFs will be saved in a new folder inside `output/` with the format:
```
output/{OPERATION}_{DRONE}_{COUNT}_{TIMESTAMP}/
```

Each folder contains:
- `checklist.pdf` - A5 field checklist with checkboxes
- `procedures.pdf` - A4 detailed procedure manual

Previous generations are automatically moved to `output/archive/` to keep things organized.

Example:
```
output/
├── VLOS_DJI_SINGLE_20251028_143012/  ← Latest
│   ├── checklist.pdf
│   └── procedures.pdf
└── archive/
    └── NIGHT_VLOS_PARROT_MULTIPLE_20251028_120000/
```

## What's What

- **Checklist PDF (A5)**: Compact checklist with checkboxes for field use - print and take with you!
- **Procedures PDF (A4)**: Detailed manual with full procedure descriptions for reference and training

## Customization

To add/modify procedures, edit the JSON files in `data/json/` directory.

To customize available operation types, drone platforms, or drone counts, edit `data/constants.json`.

See README.md for full documentation.
