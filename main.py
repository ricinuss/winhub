#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║  WinHub — Windows System Optimizer & Health Monitor  ║
║  Author : ricinus  (https://github.com/ricinuss)     ║
║  Inspired by Chris Titus WinUtil                     ║
╚══════════════════════════════════════════════════════╝

Usage:
    python main.py                        Interactive TUI
    python main.py --apply <profile.json> Auto-apply a profile
    python main.py --scan                 Health scan only (no UI)
    python main.py --list-profiles        List saved profiles
"""
import sys
import os
import argparse

# ── Add winhub package to path ────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
# ─────────────────────────────────────────────────────────────────────────────

from core.constants import *
from core.utils import enable_ansi, require_admin


# ──────────────────────────────────────────────────────────────────────────────
# CLI argument parser
# ──────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="winhub",
        description="WinHub — Windows System Optimizer by ricinus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                         # Launch interactive TUI
  python main.py --apply gaming_pc.json  # Auto-apply profile
  python main.py --scan                  # Print health report
  python main.py --list-profiles         # List saved profiles
  python main.py --preset safe           # Apply safe preset silently
  python main.py --preset balanced       # Apply balanced preset
  python main.py --preset extreme        # Apply extreme preset
        """
    )
    p.add_argument("--apply",         metavar="FILE",    help="Auto-apply a JSON profile")
    p.add_argument("--scan",          action="store_true", help="Run health scan, print report and exit")
    p.add_argument("--list-profiles", action="store_true", help="List all saved profiles")
    p.add_argument("--preset",        choices=["safe","balanced","extreme","gaming"],
                                      help="Apply a built-in preset non-interactively")
    p.add_argument("--no-admin-check",action="store_true", help="Skip admin elevation check")
    return p


# ──────────────────────────────────────────────────────────────────────────────
# Non-interactive / headless modes
# ──────────────────────────────────────────────────────────────────────────────

def cmd_scan_only():
    """Print health scan results as plain text."""
    print(f"\n{BOLD}{BR_CYAN} WinHub — System Health Scan{RESET}\n")

    from scanners.health_aggregator import run_all_scanners

    report = {}
    steps_done = []

    def cb(name, pct):
        if name != "done" and name not in steps_done:
            steps_done.append(name)
            print(f"  Scanning {name}…", end="\r")

    report = run_all_scanners(progress_cb=cb)
    print(" " * 40, end="\r")

    summary = report.get("_summary", {})
    score   = summary.get("overall_score", 0)
    grade   = summary.get("grade", "?")

    print(f"\n  System Health : {BOLD}{score:.1f}%{RESET}")
    print(f"  System Rating : {BOLD}{grade}{RESET}\n")

    for key in ("cpu","ram","disk","startup","services","power","temperature"):
        sec = report.get(key, {})
        s   = sec.get("score", 50)
        col = BR_GREEN if s >= 80 else (BR_YELLOW if s >= 60 else BR_RED)
        print(f"  {col}{key.upper():<14}{RESET}  Score {s:5.1f}")

    issues = summary.get("issues", [])
    if issues:
        print(f"\n  {BR_YELLOW}Issues:{RESET}")
        for iss in issues:
            print(f"    ⚠  {iss}")
    else:
        print(f"\n  {BR_GREEN}✔  No issues detected{RESET}")

    print()


def cmd_list_profiles():
    from profiles.manager import list_profiles
    profiles = list_profiles()
    if not profiles:
        print("No saved profiles.")
        return
    print(f"\n  {'NAME':<25}  {'TWEAKS':>6}  {'CREATED':<12}  FILE")
    print("  " + "─" * 72)
    for p in profiles:
        print(f"  {p['name']:<25}  {len(p['tweaks']):>6}  {p.get('created_at','')[:10]:<12}  {p['file']}")
    print()


def cmd_apply_profile(path: str):
    from profiles.manager import load_profile
    from optimizers.applier import apply_tweaks_batch
    from optimizers.tweaks_db import get_tweak_by_id

    if not os.path.isfile(path):
        print(f"{BR_RED}Profile not found: {path}{RESET}")
        sys.exit(1)

    data     = load_profile(path)
    name     = data.get("name", path)
    tweak_ids = data.get("tweaks", [])

    print(f"\n{BOLD}{BR_CYAN} WinHub — Applying Profile: {name}{RESET}")
    print(f"  {DIM}{len(tweak_ids)} tweaks  •  {data.get('description','')}{RESET}\n")

    def progress_cb(tname, pct):
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  [{bar}] {pct:3d}%  {tname[:40]}", end="\r")

    results = apply_tweaks_batch(tweak_ids, progress_cb=progress_cb)
    print("\n")

    ok  = sum(1 for r in results if r.success)
    bad = sum(1 for r in results if not r.success)
    print(f"  {BR_GREEN}✔  {ok} tweaks applied{RESET}")
    if bad:
        print(f"  {BR_RED}✘  {bad} tweaks failed{RESET}")
        for r in results:
            if not r.success:
                print(f"     {DIM}{r.name}: {', '.join(r.errors)}{RESET}")
    print(f"\n  {YELLOW}⚠  Restart recommended to finalize all changes.{RESET}\n")


def cmd_apply_preset(preset_name: str):
    from optimizers.tweaks_db import PRESET_SAFE, PRESET_BALANCED, PRESET_EXTREME, PRESET_GAMING

    presets = {
        "safe":     PRESET_SAFE,
        "balanced": PRESET_BALANCED,
        "extreme":  PRESET_EXTREME,
        "gaming":   PRESET_GAMING,
    }
    ids = presets.get(preset_name, [])
    if not ids:
        print(f"Unknown preset: {preset_name}")
        sys.exit(1)

    from profiles.manager import save_profile
    import tempfile, json
    tmp = os.path.join(tempfile.gettempdir(), f"winhub_{preset_name}.json")
    save_profile(preset_name, ids)
    cmd_apply_profile(os.path.join(
        ROOT, "profiles", f"{preset_name}.json"
    ))


# ──────────────────────────────────────────────────────────────────────────────
# Interactive TUI main loop
# ──────────────────────────────────────────────────────────────────────────────

def run_interactive():
    from ui.menus import (
        draw_main_menu, wait_key_main,
        run_health_scan_ui, show_health_report,
        run_apply_preset_ui, run_custom_mode_ui,
        run_profile_manager_ui, _hide_cursor,
    )
    from optimizers.tweaks_db import PRESET_SAFE, PRESET_BALANCED, PRESET_EXTREME

    _hide_cursor()
    last_report = None

    while True:
        draw_main_menu(last_report)
        choice = wait_key_main()

        if choice == '1':
            last_report = run_health_scan_ui()
            show_health_report(last_report)

        elif choice == '2':
            run_apply_preset_ui("Safe Optimization", PRESET_SAFE)

        elif choice == '3':
            run_apply_preset_ui("Balanced Optimization", PRESET_BALANCED)

        elif choice == '4':
            run_apply_preset_ui("Extreme Optimization", PRESET_EXTREME)

        elif choice == '5':
            run_custom_mode_ui()

        elif choice == '6':
            run_profile_manager_ui()

        elif choice == 'Q':
            import sys
            sys.stdout.write("\033[?25h")  # restore cursor
            print(f"\n  {BR_CYAN}Thanks for using WinHub — by ricinus{RESET}")
            print(f"  {DIM}https://github.com/ricinuss{RESET}\n")
            sys.exit(0)


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main():
    enable_ansi()

    parser = build_parser()
    args   = parser.parse_args()

    if not args.no_admin_check:
        require_admin()

    if args.scan:
        cmd_scan_only()

    elif args.list_profiles:
        cmd_list_profiles()

    elif args.apply:
        cmd_apply_profile(args.apply)

    elif args.preset:
        cmd_apply_preset(args.preset)

    else:
        run_interactive()


if __name__ == "__main__":
    main()
