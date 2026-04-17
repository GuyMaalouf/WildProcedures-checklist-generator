# Quick Start Guide

## 1) Install

```bash
pip install -r requirements.txt
```

## 2) Generate Your First PDFs

```bash
python generate_checklist.py
```

This uses the default `wild` profile and creates:

- `checklist.pdf` (A5 field checklist)
- `procedures.pdf` (A4 detailed procedures)

If you want to see the available options first:

```bash
python generate_checklist.py --list-options
python generate_checklist.py --list-profiles
```

## 3) Use Interactive Mode

```bash
python interactive_generator.py
```

The interactive menu can:

- select a profile
- select operation/platform/fleet settings
- create, duplicate, rename, inspect, or delete profiles
- go back at each selection step without restarting

## 4) Create a Custom Profile

```bash
python generate_checklist.py --create-profile my_ops --from-profile template
```

Then edit files in:

- `data/profiles/my_ops/constants.json`
- `data/profiles/my_ops/json/*.json`
- `data/profiles/my_ops/assembly/*.json` (optional)

Assembly files are only used for platform-specific setup content.

## 5) Generate from a Specific Profile

```bash
python generate_checklist.py --profile my_ops
```

You can also pass explicit options:

```bash
python generate_checklist.py --profile my_ops -o VLOS -d GENERIC -c SINGLE
```

If you are advanced and need to point at custom folders directly:

```bash
python generate_checklist.py --profile my_ops --json-dir /path/to/json
python generate_all.py --profile my_ops --json-dir /path/to/json --constants-file /path/to/constants.json --assembly-dir /path/to/assembly
```

## 6) Useful Commands

List profiles:

```bash
python generate_checklist.py --list-profiles
```

List available options for a profile:

```bash
python generate_checklist.py --profile wild --list-options
```

Bulk generation with preset matrix:

```bash
python generate_all.py --profile wild
```

The bulk generator also accepts `--json-dir`, `--constants-file`, and `--assembly-dir` overrides.

## Output Behavior

Each run creates a new folder:

```text
output/{OPERATION}_{DRONE}_{COUNT}_{TIMESTAMP}/
```

Previous output folders are archived under `output/archive/`.

## Notes

- The bundled `wild` profile is the public default.
- The `template` profile is the safest starting point for new custom data.
- There is no separate dry-run command; generation writes PDFs immediately.
