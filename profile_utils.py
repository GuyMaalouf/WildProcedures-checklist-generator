#!/usr/bin/env python3
"""Utilities for working with procedure profiles and data directories."""

import os
import re
import shutil
import json
from typing import Dict, List


DEFAULT_PROFILE = "wild"
PROFILE_ROOT = os.path.join("data", "profiles")
LOCKED_PROFILES = {DEFAULT_PROFILE, "template"}


def _script_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def sanitize_profile_name(name: str) -> str:
    """Convert user input into a safe profile directory name."""
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", name.strip().lower())
    cleaned = cleaned.strip("_")
    return cleaned


def get_profile_root(script_dir: str) -> str:
    return os.path.join(script_dir, PROFILE_ROOT)


def list_profiles(script_dir: str) -> List[str]:
    """Return profile names that contain at least constants.json and a json folder."""
    root = get_profile_root(script_dir)
    if not os.path.isdir(root):
        return []

    profiles = []
    for entry in sorted(os.listdir(root)):
        profile_dir = os.path.join(root, entry)
        if not os.path.isdir(profile_dir):
            continue
        constants_file = os.path.join(profile_dir, "constants.json")
        json_dir = os.path.join(profile_dir, "json")
        if os.path.exists(constants_file) and os.path.isdir(json_dir):
            profiles.append(entry)

    return profiles


def profile_exists(script_dir: str, profile_name: str) -> bool:
    return profile_name in list_profiles(script_dir)


def is_locked_profile(profile_name: str) -> bool:
    return profile_name in LOCKED_PROFILES


def profile_paths(script_dir: str, profile_name: str) -> Dict[str, str]:
    profile_dir = os.path.join(get_profile_root(script_dir), profile_name)
    return {
        "profile_dir": profile_dir,
        "constants_file": os.path.join(profile_dir, "constants.json"),
        "json_dir": os.path.join(profile_dir, "json"),
        "assembly_dir": os.path.join(profile_dir, "assembly"),
    }


def summarize_profile(script_dir: str, profile_name: str) -> Dict[str, object]:
    paths = profile_paths(script_dir, profile_name)
    if not os.path.isdir(paths["profile_dir"]):
        raise ValueError(f"Profile '{profile_name}' does not exist.")

    constants = {}
    if os.path.exists(paths["constants_file"]):
        with open(paths["constants_file"], "r", encoding="utf-8") as handle:
            constants = json.load(handle)

    json_files = []
    if os.path.isdir(paths["json_dir"]):
        json_files = sorted(name for name in os.listdir(paths["json_dir"]) if name.endswith(".json"))

    assembly_files = []
    if os.path.isdir(paths["assembly_dir"]):
        assembly_files = sorted(name for name in os.listdir(paths["assembly_dir"]) if name.endswith(".json"))

    return {
        "profile_name": profile_name,
        "profile_dir": paths["profile_dir"],
        "constants_file": paths["constants_file"],
        "json_dir": paths["json_dir"],
        "assembly_dir": paths["assembly_dir"],
        "json_files": json_files,
        "assembly_files": assembly_files,
        "operation_type_count": len(constants.get("operation_types", [])),
        "drone_platform_count": len(constants.get("drone_platforms", [])),
        "number_of_drones_count": len(constants.get("number_of_drones", [])),
    }


def legacy_paths(script_dir: str) -> Dict[str, str]:
    return {
        "profile_dir": os.path.join(script_dir, "data"),
        "constants_file": os.path.join(script_dir, "data", "constants.json"),
        "json_dir": os.path.join(script_dir, "data", "json"),
        "assembly_dir": os.path.join(script_dir, "data", "assembly"),
    }


def resolve_data_paths(
    script_dir: str,
    profile_name: str = DEFAULT_PROFILE,
    json_dir_override: str = None,
    constants_file_override: str = None,
    assembly_dir_override: str = None,
) -> Dict[str, str]:
    """Resolve paths for constants/json/assembly from profile and optional overrides."""
    profiles = list_profiles(script_dir)

    if profile_name in profiles:
        paths = profile_paths(script_dir, profile_name)
        source = "profile"
    elif profile_name == DEFAULT_PROFILE:
        # Backward compatibility for repos still using data/json directly.
        paths = legacy_paths(script_dir)
        source = "legacy"
    else:
        available = ", ".join(profiles) if profiles else "none"
        raise ValueError(f"Unknown profile '{profile_name}'. Available profiles: {available}")

    if json_dir_override:
        paths["json_dir"] = json_dir_override
    if constants_file_override:
        paths["constants_file"] = constants_file_override
    if assembly_dir_override:
        paths["assembly_dir"] = assembly_dir_override

    paths["source"] = source
    paths["profile_name"] = profile_name
    return paths


def _copy_tree_contents(src_dir: str, dst_dir: str) -> None:
    if not os.path.isdir(src_dir):
        return
    os.makedirs(dst_dir, exist_ok=True)
    for name in os.listdir(src_dir):
        src_path = os.path.join(src_dir, name)
        dst_path = os.path.join(dst_dir, name)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dst_path)


def create_profile(script_dir: str, profile_name: str, from_profile: str = "template") -> Dict[str, str]:
    """Create a new profile by copying from an existing profile."""
    safe_name = sanitize_profile_name(profile_name)
    if not safe_name:
        raise ValueError("Profile name must contain letters, numbers, underscores, or hyphens.")

    root = get_profile_root(script_dir)
    os.makedirs(root, exist_ok=True)

    target_paths = profile_paths(script_dir, safe_name)
    if os.path.exists(target_paths["profile_dir"]):
        raise ValueError(f"Profile '{safe_name}' already exists.")

    os.makedirs(target_paths["profile_dir"], exist_ok=True)
    os.makedirs(target_paths["json_dir"], exist_ok=True)
    os.makedirs(target_paths["assembly_dir"], exist_ok=True)

    source_paths = None
    profiles = list_profiles(script_dir)
    if from_profile in profiles:
        source_paths = profile_paths(script_dir, from_profile)
    elif from_profile == DEFAULT_PROFILE:
        source_paths = legacy_paths(script_dir)

    if source_paths is None:
        raise ValueError(f"Source profile '{from_profile}' does not exist.")

    if os.path.exists(source_paths["constants_file"]):
        shutil.copy2(source_paths["constants_file"], target_paths["constants_file"])

    _copy_tree_contents(source_paths["json_dir"], target_paths["json_dir"])
    _copy_tree_contents(source_paths["assembly_dir"], target_paths["assembly_dir"])

    return target_paths


def duplicate_profile(script_dir: str, source_profile: str, new_profile_name: str) -> Dict[str, str]:
    return create_profile(script_dir, new_profile_name, from_profile=source_profile)


def rename_profile(script_dir: str, old_profile_name: str, new_profile_name: str) -> Dict[str, str]:
    if is_locked_profile(old_profile_name):
        raise ValueError(f"Profile '{old_profile_name}' is built in and cannot be renamed.")

    safe_new_name = sanitize_profile_name(new_profile_name)
    if not safe_new_name:
        raise ValueError("Profile name must contain letters, numbers, underscores, or hyphens.")

    source_paths = profile_paths(script_dir, old_profile_name)
    target_paths = profile_paths(script_dir, safe_new_name)

    if not os.path.isdir(source_paths["profile_dir"]):
        raise ValueError(f"Profile '{old_profile_name}' does not exist.")
    if os.path.exists(target_paths["profile_dir"]):
        raise ValueError(f"Profile '{safe_new_name}' already exists.")

    os.rename(source_paths["profile_dir"], target_paths["profile_dir"])
    return target_paths


def delete_profile(script_dir: str, profile_name: str) -> None:
    if is_locked_profile(profile_name):
        raise ValueError(f"Profile '{profile_name}' is built in and cannot be deleted.")

    paths = profile_paths(script_dir, profile_name)
    if not os.path.isdir(paths["profile_dir"]):
        raise ValueError(f"Profile '{profile_name}' does not exist.")

    shutil.rmtree(paths["profile_dir"])
