"""
WinHub — Interactive Menus (keyboard navigation, checkboxes)
Author: ricinus (https://github.com/ricinuss)
"""
import sys
import os
import msvcrt
from core.constants import *
from ui.renderer import (
    draw_banner, draw_section_header, draw_metric_row,
    draw_score_badge, draw_issues, draw_apply_result,
    draw_progress_bar_animated, render_checklist_item,
    make_progress_bar, Spinner, print_line, W,
)


# ──────────────────────────────────────────────────────────────────────────────
# Low-level key reader
# ──────────────────────────────────────────────────────────────────────────────

def _read_key() -> int:
    """Read a single keypress and return the virtual key code."""
    ch = msvcrt.getch()
    if ch in (b'\x00', b'\xe0'):   # special key prefix
        ch2 = msvcrt.getch()
        return ord(ch2) + 256       # offset to avoid collision
    return ord(ch)


KEY_UP    = 72  + 256
KEY_DOWN  = 80  + 256
KEY_LEFT  = 75  + 256
KEY_RIGHT = 77  + 256
KEY_ENTER = 13
KEY_SPACE = 32
KEY_ESC   = 27
KEY_BACK  = 8
KEY_q     = ord('q')
KEY_Q     = ord('Q')
KEY_a     = ord('a')
KEY_A     = ord('A')
KEY_s     = ord('s')
KEY_S     = ord('S')
KEY_e     = ord('e')
KEY_E     = ord('E')
KEY_d     = ord('d')
KEY_D     = ord('D')
KEY_i     = ord('i')
KEY_I     = ord('I')
KEY_r     = ord('r')
KEY_R     = ord('R')


def _hide_cursor():
    sys.stdout.write("\033[?25l"); sys.stdout.flush()

def _show_cursor():
    sys.stdout.write("\033[?25h"); sys.stdout.flush()


# ──────────────────────────────────────────────────────────────────────────────
# Main menu
# ──────────────────────────────────────────────────────────────────────────────

MAIN_MENU_ITEMS = [
    ("1", "System Health Scan",        "Scan CPU, RAM, disk, services & power"),
    ("2", "Safe Optimization",         "Apply safe, risk-free tweaks"),
    ("3", "Balanced Optimization",     "Moderate tweaks for everyday use"),
    ("4", "Extreme Optimization",      "Aggressive performance tweaks"),
    ("5", "Custom Mode",               "Pick tweaks + save/load profiles"),
    ("6", "Profile Manager",           "Load / import / export profiles"),
    ("Q", "Quit",                      "Exit WinHub"),
]


def draw_main_menu(last_report=None):
    os.system("cls")
    draw_banner()

    w = W()
    draw_section_header("MAIN MENU", BR_CYAN)
    print_line()

    for key, label, desc in MAIN_MENU_ITEMS:
        kc    = f"{BG_CYAN}{BLACK}{BOLD} {key} {RESET}"
        lbl   = f"{BOLD}{BR_WHITE}{label:<30}{RESET}"
        dsc   = f"{DIM}{desc}{RESET}"
        print_line(f"    {kc}  {lbl}  {dsc}")

    if last_report:
        summary = last_report.get("_summary", {})
        score   = summary.get("overall_score", 0)
        grade   = summary.get("grade", "?")
        gc      = summary.get("grade_color", WHITE)
        print_line()
        print_line(f"  {DIM}Last scan: {gc}{BOLD}Health {score:.1f}% — Grade {grade}{RESET}")

    print_line()
    print_line(f"  {DIM}Use number keys to navigate  •  Q to quit{RESET}")
    print_line()


def wait_key_main() -> str:
    while True:
        k = _read_key()
        if k in (ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6')):
            return chr(k)
        if k in (KEY_q, KEY_Q, KEY_ESC):
            return 'Q'


# ──────────────────────────────────────────────────────────────────────────────
# Health Report Screen
# ──────────────────────────────────────────────────────────────────────────────

def show_health_report(report: dict):
    os.system("cls")
    draw_banner()
    draw_section_header("SYSTEM HEALTH REPORT", BR_CYAN)
    print_line()

    summary    = report.get("_summary", {})
    score      = summary.get("overall_score", 0)
    grade      = summary.get("grade", "?")
    grade_col  = summary.get("grade_color", WHITE)

    draw_score_badge(score, grade, grade_col)
    print_line()
    draw_section_header("DETAILED METRICS", CYAN)
    print_line()

    # CPU
    cpu = report.get("cpu", {})
    cpu_val = f"{cpu.get('usage_pct',0):.0f}% load  {cpu.get('cores',0)}C/{cpu.get('threads',0)}T  {cpu.get('speed_ghz',0):.1f} GHz"
    draw_metric_row("CPU", cpu_val, cpu.get("score", 50))

    # RAM
    ram = report.get("ram", {})
    ram_val = f"{ram.get('used_gb',0):.1f}/{ram.get('total_gb',0):.1f} GB  {ram.get('usage_pct',0):.0f}%  {ram.get('type','?')} @ {ram.get('speed_mhz',0)} MHz"
    draw_metric_row("RAM", ram_val, ram.get("score", 50))

    # Disk
    disk = report.get("disk", {})
    drives = disk.get("drives", [])
    if drives:
        d0 = drives[0]
        disk_val = f"{d0.get('letter','?')} {d0.get('type','?')}  {d0.get('used_gb',0):.1f}/{d0.get('size_gb',0):.1f} GB  {d0.get('usage_pct',0):.0f}%"
        if len(drives) > 1:
            disk_val += f"  (+{len(drives)-1} more)"
    else:
        disk_val = "No drives detected"
    draw_metric_row("Disk", disk_val, disk.get("score", 50))

    # Startup
    su = report.get("startup", {})
    su_val = f"{su.get('total',0)} startup entries"
    draw_metric_row("Startup Impact", su_val, su.get("score", 50))

    # Services
    sv = report.get("services", {})
    sv_val = f"{sv.get('total_running',0)} running  •  {len(sv.get('bloat_running',[]))} bloat active"
    draw_metric_row("Services", sv_val, sv.get("score", 50))

    # Power
    pw = report.get("power", {})
    batt = pw.get("battery_pct", -1)
    batt_str = f"  •  Battery {batt}%" if batt >= 0 else ""
    pw_val = f"{pw.get('plan_name','?')}{batt_str}"
    draw_metric_row("Power Plan", pw_val, pw.get("score", 50))

    # Temp
    tp = report.get("temperature", {})
    if tp.get("available"):
        tp_val = f"{tp.get('cpu_temp_c',0):.1f}°C"
        draw_metric_row("CPU Temp", tp_val, tp.get("score", 100))

    print_line()
    draw_section_header("ISSUES DETECTED", BR_YELLOW)
    print_line()
    draw_issues(summary.get("issues", []))
    print_line()

    # Extra drives
    if len(drives) > 1:
        draw_section_header("ALL DRIVES", CYAN)
        print_line()
        for d in drives:
            bar = make_progress_bar(d.get("usage_pct", 0), 20)
            print_line(f"  {BOLD}{d['letter']}{RESET}  {d['type']:<5}  {d['used_gb']:.1f}/{d['size_gb']:.1f} GB  {bar}  {DIM}{d['model'][:30]}{RESET}")
        print_line()

    print_line(f"  {DIM}Press any key to return to menu…{RESET}")
    _read_key()


# ──────────────────────────────────────────────────────────────────────────────
# Running health scan with live progress
# ──────────────────────────────────────────────────────────────────────────────

def run_health_scan_ui() -> dict:
    os.system("cls")
    draw_banner()
    draw_section_header("SCANNING SYSTEM…", BR_CYAN)
    print_line()

    SCAN_LABELS = {
        "cpu":         "CPU Performance",
        "ram":         "RAM Usage",
        "disk":        "Disk Health",
        "startup":     "Startup Entries",
        "services":    "Running Services",
        "power":       "Power Settings",
        "temperature": "CPU Temperature",
        "done":        "Complete",
    }

    report = {}

    def progress_cb(name, pct):
        label = SCAN_LABELS.get(name, name.capitalize())
        draw_progress_bar_animated(label, pct)

    from scanners.health_aggregator import run_all_scanners
    report = run_all_scanners(progress_cb=progress_cb)

    sys.stdout.write("\n")
    print_line(f"  {BR_GREEN}✔  Scan complete!{RESET}")
    import time; time.sleep(0.5)
    return report


# ──────────────────────────────────────────────────────────────────────────────
# Apply preset profile with progress
# ──────────────────────────────────────────────────────────────────────────────

def run_apply_preset_ui(preset_name: str, tweak_ids: list):
    os.system("cls")
    draw_banner()
    draw_section_header(f"APPLYING: {preset_name.upper()}", BR_MAGENTA)
    print_line()
    print_line(f"  {DIM}{len(tweak_ids)} tweaks will be applied. This may take a moment…{RESET}")
    print_line()

    results = []

    def progress_cb(name, pct):
        draw_progress_bar_animated(name[:40], pct)

    def step_cb(msg):
        sys.stdout.write(f"\r  {DIM}{msg[:70]:<70}{RESET}")
        sys.stdout.flush()

    from optimizers.applier import apply_tweaks_batch
    results = apply_tweaks_batch(tweak_ids, progress_cb=progress_cb, step_cb=step_cb)

    sys.stdout.write("\n\n")
    draw_apply_result(results)

    print_line(f"  {YELLOW}⚠  Some changes require a restart to fully take effect.{RESET}")
    print_line()
    print_line(f"  {DIM}Press any key to return to menu…{RESET}")
    _read_key()
    return results


# ──────────────────────────────────────────────────────────────────────────────
# Custom mode — interactive checklist
# ──────────────────────────────────────────────────────────────────────────────

def run_custom_mode_ui():
    from optimizers.tweaks_db import TWEAKS

    selected  = set()
    cursor    = 0
    page_size = 18
    scroll    = 0

    while True:
        os.system("cls")
        draw_banner()
        draw_section_header("CUSTOM MODE — Select Tweaks", BR_MAGENTA)
        print_line(f"  {DIM}↑↓ Navigate  SPACE Select/Deselect  A=All  N=None  ENTER=Apply  S=Save  Q=Back{RESET}")
        print_line()

        visible = TWEAKS[scroll: scroll + page_size]
        for i, tweak in enumerate(visible):
            idx      = scroll + i
            focused  = (idx == cursor)
            sel      = tweak["id"] in selected
            line     = render_checklist_item(
                            tweak["name"], tweak["desc"],
                            sel, focused, tweak.get("risk", "safe"))
            print_line(line)

        print_line()
        total = len(TWEAKS)
        print_line(f"  {DIM}Selected: {BR_CYAN}{len(selected)}{RESET}{DIM}/{total}  •  Page {scroll//page_size+1}/{(total-1)//page_size+1}{RESET}")
        print_line()

        k = _read_key()

        if k == KEY_UP:
            cursor = max(0, cursor - 1)
            if cursor < scroll:
                scroll = cursor

        elif k == KEY_DOWN:
            cursor = min(len(TWEAKS) - 1, cursor + 1)
            if cursor >= scroll + page_size:
                scroll = cursor - page_size + 1

        elif k == KEY_SPACE:
            tid = TWEAKS[cursor]["id"]
            if tid in selected:
                selected.discard(tid)
            else:
                selected.add(tid)

        elif k in (KEY_a, KEY_A):
            selected = {t["id"] for t in TWEAKS}

        elif k == ord('n') or k == ord('N'):
            selected = set()

        elif k == KEY_ENTER:
            if not selected:
                print_line(f"  {BR_YELLOW}No tweaks selected.{RESET}")
                import time; time.sleep(1)
                continue
            _confirm_and_apply("Custom Selection", list(selected))
            break

        elif k in (KEY_s, KEY_S):
            _save_profile_ui(list(selected))

        elif k in (KEY_q, KEY_Q, KEY_ESC):
            break


def _confirm_and_apply(preset_name: str, tweak_ids: list):
    os.system("cls")
    draw_banner()
    print_line(f"\n  {BR_YELLOW}⚠  You are about to apply {BOLD}{len(tweak_ids)} tweaks{RESET}{BR_YELLOW}.{RESET}")
    print_line(f"  {DIM}A system restore point is recommended before proceeding.{RESET}")
    print_line()
    print_line(f"  {BOLD}Proceed? [Y/N]{RESET} ", end="")
    sys.stdout.flush()
    ch = _read_key()
    if ch in (ord('y'), ord('Y')):
        run_apply_preset_ui(preset_name, tweak_ids)


def _save_profile_ui(tweak_ids: list):
    from profiles.manager import save_profile
    _show_cursor()
    os.system("cls")
    draw_banner()
    draw_section_header("SAVE PROFILE", BR_CYAN)
    print_line()
    print_line(f"  {BOLD}Profile name:{RESET} ", end="")
    sys.stdout.flush()
    name = input().strip()
    if not name:
        _hide_cursor()
        return
    print_line(f"  {DIM}Description (optional):{RESET} ", end="")
    sys.stdout.flush()
    desc = input().strip()
    path = save_profile(name, tweak_ids, desc)
    print_line(f"\n  {BR_GREEN}✔  Saved: {path}{RESET}")
    import time; time.sleep(1.5)
    _hide_cursor()


# ──────────────────────────────────────────────────────────────────────────────
# Profile Manager Screen
# ──────────────────────────────────────────────────────────────────────────────

def run_profile_manager_ui():
    while True:
        from profiles.manager import list_profiles, delete_profile, import_profile

        os.system("cls")
        draw_banner()
        draw_section_header("PROFILE MANAGER", BR_CYAN)
        print_line()

        profiles = list_profiles()

        if not profiles:
            print_line(f"  {DIM}No saved profiles. Use Custom Mode to create one.{RESET}")
        else:
            for i, p in enumerate(profiles, 1):
                n_tweaks = len(p["tweaks"])
                print_line(f"  {BR_CYAN}{BOLD}[{i}]{RESET}  {BOLD}{p['name']:<25}{RESET}  "
                           f"{DIM}{n_tweaks} tweaks  •  {p.get('created_at','')[:10]}{RESET}")
                if p.get("description"):
                    print_line(f"       {DIM}{p['description']}{RESET}")

        print_line()
        print_line(f"  {DIM}[number] Apply profile  I=Import  Q=Back{RESET}")
        print_line()

        k = _read_key()

        if k in (KEY_q, KEY_Q, KEY_ESC):
            break

        elif k in (KEY_i, KEY_I):
            _import_profile_ui()

        elif ord('1') <= k <= ord('9'):
            idx = k - ord('1')
            if idx < len(profiles):
                p = profiles[idx]
                _confirm_and_apply(p["name"], p["tweaks"])


def _import_profile_ui():
    _show_cursor()
    os.system("cls")
    draw_banner()
    draw_section_header("IMPORT PROFILE", BR_CYAN)
    print_line()
    print_line(f"  {BOLD}Path to JSON file:{RESET} ", end="")
    sys.stdout.flush()
    path = input().strip().strip('"')
    _hide_cursor()
    if not path or not os.path.isfile(path):
        print_line(f"  {BR_RED}File not found.{RESET}")
        import time; time.sleep(1.5)
        return
    from profiles.manager import import_profile
    new_path = import_profile(path)
    print_line(f"\n  {BR_GREEN}✔  Imported to: {new_path}{RESET}")
    import time; time.sleep(1.5)
