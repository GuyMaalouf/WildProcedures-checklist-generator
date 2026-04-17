# WildProcedures Checklist Generator

Generate operation-specific drone checklists and procedure manuals as PDFs.

The repository ships with a sanitized public dataset and a starter template so teams can either use the bundled procedures or copy them into their own profile and customize from there.

## What You Get

- A compact A5 checklist PDF for field use
- A detailed A4 procedures PDF for briefing and reference
- Filtering by operation type, drone platform, and number of drones
- Profile-based data management for built-in and custom procedure sets
- Interactive terminal navigation for users who do not want to edit every command by hand

## Requirements

- Python 3.8 or later
- `fpdf==1.7.2`

## Install

```bash
pip install -r requirements.txt
```

## Quick Start

Generate the default checklist set:

```bash
python generate_checklist.py
```

Open the interactive menu:

```bash
python interactive_generator.py
```

Generate all preset bundles for a profile:

```bash
python generate_all.py --profile wild
```

## Common Commands

List available operation, drone, and fleet options:

```bash
python generate_checklist.py --list-options
```

List available profiles:

```bash
python generate_checklist.py --list-profiles
```

Create a custom profile from the starter template:

```bash
python generate_checklist.py --create-profile my_ops --from-profile template
```

Generate from a specific profile:

```bash
python generate_checklist.py --profile wild -o BVLOS_NO_VO -d DJI -c SINGLE
```

Advanced use with explicit data overrides:

```bash
python generate_checklist.py --profile wild --json-dir /path/to/json
python generate_all.py --profile wild --json-dir /path/to/json --constants-file /path/to/constants.json --assembly-dir /path/to/assembly
```

## Profiles

A profile is a reusable checklist package. It contains the option lists shown in the UI and the JSON files that become the generated PDFs.

- `wild` is the public built-in profile.
- `template` is the starter profile you should copy when building your own dataset.
- Custom profiles live under `data/profiles/<profile_name>/`.

Use the interactive menu or `--create-profile` to make a copy, then edit the copied files in your text editor.

### Profile Contents

Each profile contains:

- `constants.json` - available operation types, drone platforms, and fleet sizes
- `json/*.json` - the main procedure sections
- `assembly/*.json` - optional platform-specific assembly content that can be inserted before first flight

## How To Edit Content

Edit the JSON files directly when you want to change the actual procedures.

- Add or update options in `constants.json` when you want new labels in the UI.
- Add or update section files in `json/` when you want to change checklist content.
- Add platform-specific setup steps in `assembly/` when the content should only appear for a specific drone type.

The generator reads the JSON in document order. For the built-in profile, assembly content is inserted before the first-flight section so setup steps appear in the expected place in the PDF.

## Data Layout

```
data/
├── constants.json              # Legacy fallback
├── json/                       # Legacy fallback
├── assembly/                   # Legacy fallback
└── profiles/
    ├── README.md
    ├── template/
    │   ├── constants.json
    │   ├── json/
    │   └── assembly/
    └── wild/
        ├── constants.json
        ├── json/
        └── assembly/
```

## Procedure Format

Each procedure entry uses this shape:

```json
{
  "checklist_entry": "Brief checklist item",
  "procedure_description": "Detailed procedure guidance",
  "operation_types": ["VLOS"] or ["ALL"],
  "drone_platforms": ["GENERIC"] or ["ALL"],
  "number_of_drones": ["SINGLE"] or ["ALL"]
}
```

## Output

Each run creates a timestamped folder like this:

```text
output/{OPERATION}_{DRONE}_{COUNT}_{TIMESTAMP}/
├── checklist.pdf
└── procedures.pdf
```

Older output folders are moved to `output/archive/` automatically.

## Notes

- The repository is set up so local generated output stays out of version control.
- The bundled datasets were sanitized for public release.
- The app currently does not include a formal validation or dry-run mode.

## License

See `LICENSE`.
