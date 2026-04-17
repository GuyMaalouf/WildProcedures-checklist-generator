#!/usr/bin/env python3
"""
Interactive Checklist Generator
Prompts user for input and generates checklists
"""

import subprocess
import sys
import json
import os

from profile_utils import (
    create_profile,
    delete_profile,
    duplicate_profile,
    is_locked_profile,
    list_profiles,
    rename_profile,
    resolve_data_paths,
    summarize_profile,
)


def load_constants(constants_file):
    """Load constants from JSON file."""
    with open(constants_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def ask_choice(prompt, num_options, default="1"):
    raw = input(prompt).strip() or default
    try:
        index = int(raw)
        if 1 <= index <= num_options:
            return index
    except ValueError:
        pass
    return int(default)


def ask_choice_with_back(prompt, num_options, default="1"):
    raw = input(prompt).strip() or default
    if raw.lower() in {"b", "back", "0"}:
        return None
    try:
        index = int(raw)
        if 1 <= index <= num_options:
            return index
    except ValueError:
        pass
    return int(default)


def pause():
    input("\nPress Enter to continue...")


def choose_profile(script_dir):
    profiles = list_profiles(script_dir)
    if not profiles:
        print("No profiles found in data/profiles, using the legacy data folder instead.")
        return "wild"

    print("Procedure Profiles:")
    print("  A profile is a checklist package: it defines the options users can pick")
    print("  and the procedure library used to build the PDFs.")
    print("  wild     = ready-to-use public procedures")
    print("  template = minimal starter package for your own procedures")
    print()
    for i, profile in enumerate(profiles, 1):
        print(f"  {i}. {profile}")
    print()

    default_index = 1
    if "wild" in profiles:
        default_index = profiles.index("wild") + 1

    choice = ask_choice_with_back(
        f"Select profile (1-{len(profiles)}) or 0 to go back [{default_index}]: ",
        len(profiles),
        default=str(default_index),
    )
    if choice is None:
        return None
    return profiles[choice - 1]


def print_profile_summary(script_dir, profile_name):
    summary = summarize_profile(script_dir, profile_name)
    print(f"\nProfile: {summary['profile_name']}")
    print(f"  Locked: {'yes' if is_locked_profile(profile_name) else 'no'}")
    print(f"  JSON files: {len(summary['json_files'])}")
    print(f"  Assembly files: {len(summary['assembly_files'])}")
    print(f"  Operation types: {summary['operation_type_count']}")
    print(f"  Drone platforms: {summary['drone_platform_count']}")
    print(f"  Number of drones: {summary['number_of_drones_count']}")
    if summary['json_files']:
        print("  Procedure files:")
        for name in summary['json_files']:
            print(f"    - {name}")
    if summary['assembly_files']:
        print("  Assembly files:")
        for name in summary['assembly_files']:
            print(f"    - {name}")


def manage_profiles_flow(script_dir):
    while True:
        print("Profile Management:")
        print("  1. List profiles")
        print("  2. Inspect profile")
        print("  3. Create profile")
        print("  4. Duplicate profile")
        print("  5. Rename profile")
        print("  6. Delete profile")
        print("  7. Back")
        print()

        choice = ask_choice_with_back("Select option (1-7) [1]: ", 7, default="1")
        print()

        if choice is None or choice == 7:
            return

        profiles = list_profiles(script_dir)

        if choice == 1:
            if not profiles:
                print("No profiles found.")
            else:
                print("Available profiles:")
                for profile in profiles:
                    lock_label = " (built in)" if is_locked_profile(profile) else ""
                    print(f"  - {profile}{lock_label}")
            pause()
            print()
            continue

        if choice == 2:
            profile = choose_profile(script_dir)
            if profile is None:
                print()
                continue
            print_profile_summary(script_dir, profile)
            pause()
            print()
            continue

        if choice == 3:
            create_profile_flow(script_dir)
            pause()
            print()
            continue

        if choice == 4:
            source = choose_profile(script_dir)
            if source is None:
                print()
                continue
            target_name = input("Enter new profile name: ").strip()
            if not target_name:
                print("Canceled: profile name is required.")
                pause()
                print()
                continue
            try:
                created = duplicate_profile(script_dir, source, target_name)
                print(f"\n✓ Profile duplicated: {os.path.basename(created['profile_dir'])}")
            except ValueError as error:
                print(f"\nError: {error}")
            pause()
            print()
            continue

        if choice == 5:
            profile = choose_profile(script_dir)
            if profile is None:
                print()
                continue
            if is_locked_profile(profile):
                print(f"Profile '{profile}' is built in and cannot be renamed.")
                pause()
                print()
                continue
            new_name = input("Enter new profile name: ").strip()
            if not new_name:
                print("Canceled: profile name is required.")
                pause()
                print()
                continue
            try:
                renamed = rename_profile(script_dir, profile, new_name)
                print(f"\n✓ Profile renamed to: {os.path.basename(renamed['profile_dir'])}")
            except ValueError as error:
                print(f"\nError: {error}")
            pause()
            print()
            continue

        if choice == 6:
            profile = choose_profile(script_dir)
            if profile is None:
                print()
                continue
            if is_locked_profile(profile):
                print(f"Profile '{profile}' is built in and cannot be deleted.")
                pause()
                print()
                continue
            confirm = input(f"Type DELETE to remove '{profile}': ").strip()
            if confirm != "DELETE":
                print("Canceled.")
                pause()
                print()
                continue
            try:
                delete_profile(script_dir, profile)
                print(f"\n✓ Profile deleted: {profile}")
            except ValueError as error:
                print(f"\nError: {error}")
            pause()
            print()
            continue


def create_profile_flow(script_dir):
    print("Create a new checklist package by copying an existing one.")
    print("Use this when you want your own procedures, labels, and operating style")
    print("without changing the bundled public package.")
    print()

    profile_name = input("Enter new profile name (e.g. my_team): ").strip()
    if not profile_name:
        print("Canceled: profile name is required.")
        return

    source = input("Copy from which profile? [template]: ").strip() or "template"
    try:
        created = create_profile(script_dir, profile_name, from_profile=source)
        print(f"\n✓ Profile created: {os.path.basename(created['profile_dir'])}")
        print(f"  Edit JSON files in: {created['json_dir']}")
        print(f"  Edit constants in: {created['constants_file']}\n")
        print("Next steps:")
        print("  1. Add or edit procedure steps for your workflow")
        print("  2. Adjust available options (operation/platform/fleet) if needed")
        print("  3. Run the generator again and select your new profile")
    except ValueError as e:
        print(f"\nError: {e}\n")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        print("=" * 60)
        print("  Drone Operations Checklist Generator")
        print("=" * 60)
        print()
        print("This tool builds two documents:")
        print("  - a compact field checklist")
        print("  - a detailed procedures document")
        print()
        print("Profiles are checklist packages. Use the built-in ones or create your own.")
        print()

        print("1. Generate checklists")
        print("2. Manage profiles")
        print("3. Exit")
        print()
        top_choice = ask_choice("Select option (1-3) [1]: ", 3, default="1")
        print()

        if top_choice == 3:
            print("Goodbye.")
            return

        if top_choice == 2:
            manage_profiles_flow(script_dir)
            continue

        profile = choose_profile(script_dir)
        if profile is None:
            print("Returning to main menu.")
            print()
            continue

        try:
            paths = resolve_data_paths(script_dir, profile_name=profile)
        except ValueError as error:
            print(f"Error: {error}")
            pause()
            print()
            continue

        constants = load_constants(paths['constants_file'])

        print("Operation Types:")
        print("  Pick the flight scenario you want to generate documents for.")
        op_choices = constants['operation_types']
        for i, (code, name) in enumerate(op_choices, 1):
            print(f"  {i}. {code:15} - {name}")
        print()
        op_choice = ask_choice_with_back(f"Select operation type (1-{len(op_choices)}) or 0 to go back [1]: ", len(op_choices), default="1")
        if op_choice is None:
            print("Returning to main menu.")
            print()
            continue
        try:
            operation = op_choices[op_choice - 1][0]
        except (ValueError, IndexError):
            operation = op_choices[0][0]

        print()
        print("Drone Platforms:")
        print("  Pick the aircraft or platform these procedures should target.")
        drone_choices = constants['drone_platforms']
        for i, (code, name) in enumerate(drone_choices, 1):
            print(f"  {i}. {code:15} - {name}")
        print()
        drone_choice = ask_choice_with_back(f"Select drone platform (1-{len(drone_choices)}) or 0 to go back [1]: ", len(drone_choices), default="1")
        if drone_choice is None:
            print("Returning to main menu.")
            print()
            continue
        try:
            drone = drone_choices[drone_choice - 1][0]
        except (ValueError, IndexError):
            drone = drone_choices[0][0]

        print()
        print("Number of Drones:")
        print("  This controls whether the output is for a single aircraft, multiple aircraft, or a swarm.")
        count_choices = constants['number_of_drones']
        for i, (code, name) in enumerate(count_choices, 1):
            print(f"  {i}. {code:15} - {name}")
        print()
        count_choice = ask_choice_with_back(f"Select number of drones (1-{len(count_choices)}) or 0 to go back [1]: ", len(count_choices), default="1")
        if count_choice is None:
            print("Returning to main menu.")
            print()
            continue
        try:
            count = count_choices[count_choice - 1][0]
        except (ValueError, IndexError):
            count = count_choices[0][0]

        print()
        print("=" * 60)
        print("Generating checklists for:")
        print(f"  Profile: {profile}")
        print(f"  Operation: {operation}")
        print(f"  Drone: {drone}")
        print(f"  Count: {count}")
        print("=" * 60)
        print()
        print("The generator will write PDFs into an output folder named with the current timestamp.")
        print()

        cmd = [
            sys.executable,
            "generate_checklist.py",
            "--profile",
            profile,
            "-o",
            operation,
            "-d",
            drone,
            "-c",
            count,
        ]
        subprocess.run(cmd)
        print()
        pause()
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCanceled by user.")
        sys.exit(0)
