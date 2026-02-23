#!/usr/bin/env python3
"""
Bulk Checklist Generator
Generates all standard operation checklists and procedures in a single dated folder.

Output structure:
    output/
    └── YYYYMMDD/
        ├── Json/               ← snapshot of all JSON source files
        ├── VLOS/
        │   ├── checklist.pdf
        │   └── procedures.pdf
        ├── BVLOS_No_Vo/
        ├── BVLOS_Vo/
        ├── Night/
        ├── Swarm/
        └── Multi-UAS/

Usage:
    python generate_all.py
"""

import os
import sys
import shutil
from datetime import datetime

# Import the generator and helpers from the existing module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_checklist import ChecklistGenerator, get_json_files


# ─── Operations to generate ───────────────────────────────────────────────────
# Each entry defines: output folder name, operation_type, drone_platform, number_of_drones
OPERATIONS = [
    {
        "folder":           "01-VLOS",
        "operation_type":   "VLOS",
        "drone_platform":   "DJI",
        "number_of_drones": "SINGLE",
        "label":            "VLOS | DJI | Single",
    },
    {
        "folder":           "02-BVLOS_No_Vo",
        "operation_type":   "BVLOS_NO_VO",
        "drone_platform":   "DJI",
        "number_of_drones": "SINGLE",
        "label":            "BVLOS No VO | DJI | Single",
    },
    {
        "folder":           "03-BVLOS_Vo",
        "operation_type":   "BVLOS_VO",
        "drone_platform":   "DJI",
        "number_of_drones": "SINGLE",
        "label":            "BVLOS VO | DJI | Single",
    },
    {
        "folder":           "04-Night",
        "operation_type":   "NIGHT_BVLOS",
        "drone_platform":   "DJI",
        "number_of_drones": "SINGLE",
        "label":            "Night BVLOS | DJI | Single",
    },
    {
        "folder":           "05-Swarm",
        "operation_type":   "BVLOS_NO_VO",
        "drone_platform":   "DJI",
        "number_of_drones": "SWARM",
        "label":            "BVLOS No VO | DJI | Swarm",
    },
    {
        "folder":           "06-Multi-UAS",
        "operation_type":   "BVLOS_NO_VO",
        "drone_platform":   "DJI",
        "number_of_drones": "MULTIPLE",
        "label":            "BVLOS No VO | DJI | Multiple",
    },
]
# ──────────────────────────────────────────────────────────────────────────────


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_dir   = os.path.join(script_dir, 'data', 'json')
    output_dir = os.path.join(script_dir, 'output')

    # ── Dated root folder ─────────────────────────────────────────────────────
    today        = datetime.now().strftime("%Y%m%d_%H%M")
    dated_folder = os.path.join(output_dir, today)
    os.makedirs(dated_folder, exist_ok=True)

    print()
    print("=" * 60)
    print("  Bulk Checklist Generator")
    print("=" * 60)
    print(f"  Date   : {today}")
    print(f"  Output : output/{today}/")
    print("=" * 60)
    print()

    # ── Load JSON files ───────────────────────────────────────────────────────
    json_files = get_json_files(json_dir)
    if not json_files:
        print(f"Error: No JSON files found in {json_dir}")
        sys.exit(1)
    print(f"  {len(json_files)} JSON source files found.")
    print()

    # ── Back up JSON source files ─────────────────────────────────────────────
    json_backup_dir = os.path.join(dated_folder, '00-Json')
    os.makedirs(json_backup_dir, exist_ok=True)

    for jf in json_files:
        shutil.copy2(jf, json_backup_dir)

    # Also copy constants.json for completeness
    constants_src = os.path.join(script_dir, 'data', 'constants.json')
    if os.path.exists(constants_src):
        shutil.copy2(constants_src, json_backup_dir)

    total_files = len(json_files) + (1 if os.path.exists(constants_src) else 0)
    print(f"✓ JSON snapshot saved  → {today}/00-Json/  ({total_files} files)")
    print()

    # ── Generate each operation ───────────────────────────────────────────────
    errors = []
    for i, op in enumerate(OPERATIONS, 1):
        folder_name = op["folder"]
        op_folder   = os.path.join(dated_folder, folder_name)
        os.makedirs(op_folder, exist_ok=True)

        print(f"[{i}/{len(OPERATIONS)}] {op['label']}")
        print(f"        → {today}/{folder_name}/")

        try:
            generator = ChecklistGenerator(
                checklist_files=json_files,
                operation_type=op["operation_type"],
                drone_platform=op["drone_platform"],
                number_of_drones=op["number_of_drones"],
            )
            generator.generate_checklist_pdf(op_folder, f"{folder_name}_checklist.pdf")
            generator.generate_procedure_pdf(op_folder,  f"{folder_name}_procedures.pdf")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            errors.append((folder_name, str(e)))

        print()

    # ── Summary ───────────────────────────────────────────────────────────────
    print("=" * 60)
    if not errors:
        print("✓ All documents generated successfully!")
    else:
        print(f"  Completed with {len(errors)} error(s).")

    print(f"\n  output/{today}/")
    print(f"  ├── 00-Json/  ({total_files} files)")
    for op in OPERATIONS:
        status = "✗" if any(e[0] == op["folder"] for e in errors) else "✓"
        fn = op['folder']
        print(f"  ├── {status} {fn}/")
        print(f"  │       {fn}_checklist.pdf  |  {fn}_procedures.pdf")
    print("=" * 60)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCanceled by user.")
        sys.exit(0)
