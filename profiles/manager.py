"""
WinHub — Profile Manager
Save / load / import / export custom optimization profiles as JSON.
Author: ricinus (https://github.com/ricinuss)
"""
import json
import os
import datetime

PROFILES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "profiles")


def _ensure_dir():
    os.makedirs(PROFILES_DIR, exist_ok=True)


def list_profiles() -> list[dict]:
    """Return list of {name, path, tweaks, created_at} dicts."""
    _ensure_dir()
    profiles = []
    for fname in sorted(os.listdir(PROFILES_DIR)):
        if fname.endswith(".json"):
            path = os.path.join(PROFILES_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                profiles.append({
                    "name":       data.get("name", fname[:-5]),
                    "file":       fname,
                    "path":       path,
                    "tweaks":     data.get("tweaks", []),
                    "created_at": data.get("created_at", ""),
                    "description":data.get("description", ""),
                })
            except Exception:
                pass
    return profiles


def save_profile(name: str, tweak_ids: list, description: str = "") -> str:
    """Save a profile. Returns the path of the saved file."""
    _ensure_dir()
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in name).strip()
    fname     = safe_name.lower().replace(" ", "_") + ".json"
    path      = os.path.join(PROFILES_DIR, fname)

    data = {
        "name":        name,
        "description": description,
        "tweaks":      tweak_ids,
        "created_at":  datetime.datetime.now().isoformat(timespec="seconds"),
        "author":      "ricinus — https://github.com/ricinuss",
        "winhub_version": "1.0.0",
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def load_profile(path: str) -> dict:
    """Load a profile from a JSON file path. Returns the data dict."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_profile_by_name(name: str) -> dict | None:
    """Find and load a profile by its display name or filename stem."""
    for p in list_profiles():
        stem = p["file"][:-5]
        if p["name"].lower() == name.lower() or stem.lower() == name.lower():
            return load_profile(p["path"])
    return None


def delete_profile(name: str) -> bool:
    """Delete a profile by name. Returns True if deleted."""
    for p in list_profiles():
        stem = p["file"][:-5]
        if p["name"].lower() == name.lower() or stem.lower() == name.lower():
            try:
                os.remove(p["path"])
                return True
            except Exception:
                return False
    return False


def export_profile(name: str, dest_path: str) -> bool:
    """Copy a profile JSON to dest_path."""
    import shutil
    for p in list_profiles():
        stem = p["file"][:-5]
        if p["name"].lower() == name.lower() or stem.lower() == name.lower():
            try:
                shutil.copy2(p["path"], dest_path)
                return True
            except Exception:
                return False
    return False


def import_profile(src_path: str) -> str:
    """Import a JSON profile from src_path into profiles dir. Returns new path."""
    _ensure_dir()
    data = load_profile(src_path)
    name = data.get("name", os.path.basename(src_path)[:-5])
    return save_profile(
        name       = name,
        tweak_ids  = data.get("tweaks", []),
        description= data.get("description", ""),
    )
