#!/usr/bin/env python3
"""
Interactive Checklist Generator
Prompts user for input and generates checklists
"""

import subprocess
import sys
import json
import os


def load_constants():
    """Load constants from JSON file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    constants_file = os.path.join(script_dir, 'data/constants.json')
    
    with open(constants_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    constants = load_constants()
    
    print("=" * 60)
    print("  Drone Operations Checklist Generator")
    print("=" * 60)
    print()
    
    # Operation Types
    print("Operation Types:")
    op_choices = constants['operation_types']
    for i, (code, name) in enumerate(op_choices, 1):
        print(f"  {i}. {code:15} - {name}")
    print()
    op_choice = input(f"Select operation type (1-{len(op_choices)}) [1]: ").strip() or "1"
    try:
        operation = op_choices[int(op_choice) - 1][0]
    except (ValueError, IndexError):
        operation = op_choices[0][0]
    
    print()
    # Drone Platforms
    print("Drone Platforms:")
    drone_choices = constants['drone_platforms']
    for i, (code, name) in enumerate(drone_choices, 1):
        print(f"  {i}. {code:15} - {name}")
    print()
    drone_choice = input(f"Select drone platform (1-{len(drone_choices)}) [1]: ").strip() or "1"
    try:
        drone = drone_choices[int(drone_choice) - 1][0]
    except (ValueError, IndexError):
        drone = drone_choices[0][0]
    
    print()
    # Number of Drones
    print("Number of Drones:")
    count_choices = constants['number_of_drones']
    for i, (code, name) in enumerate(count_choices, 1):
        print(f"  {i}. {code:15} - {name}")
    print()
    count_choice = input(f"Select number of drones (1-{len(count_choices)}) [1]: ").strip() or "1"
    try:
        count = count_choices[int(count_choice) - 1][0]
    except (ValueError, IndexError):
        count = count_choices[0][0]
    
    print()
    print("=" * 60)
    print(f"Generating checklists for:")
    print(f"  Operation: {operation}")
    print(f"  Drone: {drone}")
    print(f"  Count: {count}")
    print("=" * 60)
    print()
    
    # Run the generator
    cmd = ["python", "generate_checklist.py", "-o", operation, "-d", drone, "-c", count]
    subprocess.run(cmd)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCanceled by user.")
        sys.exit(0)
