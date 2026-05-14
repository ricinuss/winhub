"""
WinHub — Core Utilities
Author: ricinus (https://github.com/ricinuss)
"""
import subprocess
import ctypes
import sys
import os
import shutil
import winreg
from core.constants import *


# ──────────────────────────────────────────────
# Terminal / ANSI Setup
# ──────────────────────────────────────────────

def enable_ansi():
    """Enable ANSI escape codes on Windows console."""
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


def get_terminal_width() -> int:
    return shutil.get_terminal_size((100, 30)).columns


def clear_screen():
    os.system("cls")


def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def move_cursor(row: int, col: int):
    sys.stdout.write(f"\033[{row};{col}H")
    sys.stdout.flush()


def save_cursor():
    sys.stdout.write("\033[s")


def restore_cursor():
    sys.stdout.write("\033[u")


# ──────────────────────────────────────────────
# Admin Check
# ──────────────────────────────────────────────

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def require_admin():
    if not is_admin():
        print(f"{BR_RED}[!] WinHub must be run as Administrator.{RESET}")
        print(f"{YELLOW}    Right-click → 'Run as administrator'{RESET}")
        sys.exit(1)


# ──────────────────────────────────────────────
# PowerShell Runner
# ──────────────────────────────────────────────

def run_powershell(script: str, capture: bool = True, timeout: int = 60) -> tuple[int, str, str]:
    """
    Run a PowerShell script string. Returns (returncode, stdout, stderr).
    Derived from WinUtil's Invoke-WinUtilScript pattern.
    """
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy", "Bypass",
        "-Command", script
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if capture else 0
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)


def run_powershell_live(script: str) -> int:
    """Run PowerShell showing output in real time."""
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-Command", script
    ]
    try:
        proc = subprocess.Popen(cmd, text=True)
        proc.wait()
        return proc.returncode
    except Exception:
        return -1


def run_command_silent(cmd: list) -> tuple[int, str]:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return result.returncode, result.stdout.strip()
    except Exception as e:
        return -1, str(e)


# ──────────────────────────────────────────────
# Registry Helpers (adapted from Set-WinUtilRegistry)
# ──────────────────────────────────────────────

_HIVE_MAP = {
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
    "HKU":  winreg.HKEY_USERS,
    "HKCC": winreg.HKEY_CURRENT_CONFIG,
}

_TYPE_MAP = {
    "DWord":        winreg.REG_DWORD,
    "QWord":        winreg.REG_QWORD,
    "String":       winreg.REG_SZ,
    "ExpandString": winreg.REG_EXPAND_SZ,
    "Binary":       winreg.REG_BINARY,
    "MultiString":  winreg.REG_MULTI_SZ,
}


def _parse_reg_path(path: str):
    """Split 'HKLM:\\\\SOFTWARE\\\\...' into (hive_handle, subkey)."""
    path = path.replace("/", "\\")
    parts = path.split("\\", 1)
    hive_str = parts[0].upper().rstrip(":")
    subkey = parts[1] if len(parts) > 1 else ""
    hive = _HIVE_MAP.get(hive_str, winreg.HKEY_LOCAL_MACHINE)
    return hive, subkey


def set_registry_value(path: str, name: str, value, reg_type: str = "DWord") -> bool:
    """Write a registry value. Returns True on success."""
    try:
        hive, subkey = _parse_reg_path(path)
        reg_type_const = _TYPE_MAP.get(reg_type, winreg.REG_DWORD)
        if reg_type in ("DWord", "QWord"):
            value = int(value)
        with winreg.CreateKeyEx(hive, subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
            winreg.SetValueEx(key, name, 0, reg_type_const, value)
        return True
    except Exception:
        return False


def get_registry_value(path: str, name: str):
    """Read a registry value. Returns (value, type) or (None, None)."""
    try:
        hive, subkey = _parse_reg_path(path)
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
            val, vtype = winreg.QueryValueEx(key, name)
            return val, vtype
    except Exception:
        return None, None


def delete_registry_value(path: str, name: str) -> bool:
    try:
        hive, subkey = _parse_reg_path(path)
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
            winreg.DeleteValue(key, name)
        return True
    except Exception:
        return False


# ──────────────────────────────────────────────
# Score/Grade Helper
# ──────────────────────────────────────────────

def score_to_grade(score: float) -> tuple[str, str]:
    """Return (grade_letter, color) for a 0-100 score."""
    for (low, high), (grade, color) in SCORE_GRADE.items():
        if low <= score < high:
            return grade, color
    return "F", RED


def score_to_color(score: float) -> str:
    if score >= 80:
        return BR_GREEN
    elif score >= 60:
        return BR_YELLOW
    elif score >= 40:
        return YELLOW
    return BR_RED


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def format_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"
