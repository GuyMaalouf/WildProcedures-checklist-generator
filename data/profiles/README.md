# Procedure Profiles

Profiles let users keep multiple procedure sets in one repository.

## Built-in Profiles

- `wild`: Bundled public dataset used by default.
- `template`: Minimal starter dataset to copy when creating a new profile.

## What A Profile Contains

Each profile in `data/profiles/<profile_name>/` contains:

- `constants.json` for the option lists shown in the UI
- `json/*.json` for the main procedure sections
- `assembly/*.json` for optional platform-specific assembly content

The generator reads the JSON files in order, and assembly content is inserted before the first-flight section when it is available.

## Common Commands

List profiles:

```bash
python generate_checklist.py --list-profiles
```

Create a custom profile from template:

```bash
python generate_checklist.py --create-profile my_ops --from-profile template
```

Then edit the copied files in your editor.

Generate from a profile:

```bash
python generate_checklist.py --profile my_ops
```

Run the interactive menu:

```bash
python interactive_generator.py
```

List available options for a profile:

```bash
python generate_checklist.py --profile wild --list-options
```
