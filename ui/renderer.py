"""
WinHub — Terminal UI Renderer
All drawing primitives: boxes, bars, badges, spinners, headers.
Author: ricinus (https://github.com/ricinuss)
"""
import sys
import time
import shutil
from core.constants import *


# ──────────────────────────────────────────────────────────────────────────────
# Width helper
# ──────────────────────────────────────────────────────────────────────────────

def W() -> int:
    return shutil.get_terminal_size((100, 30)).columns


def print_line(text: str = "", end: str = "\n"):
    sys.stdout.write(text + end)
    sys.stdout.flush()


# ──────────────────────────────────────────────────────────────────────────────
# Header / Banner
# ──────────────────────────────────────────────────────────────────────────────

BANNER = r"""
                                                       
▄▄▄▄  ▄▄▄  ▄▄▄▄           ▄▄▄   ▄▄▄ ▄▄▄  ▄▄▄ ▄▄▄▄▄▄▄   
▀███  ███  ███▀ ▀▀        ███   ███ ███  ███ ███▀▀███▄ 
 ███  ███  ███  ██  ████▄ █████████ ███  ███ ███▄▄███▀ 
 ███▄▄███▄▄███  ██  ██ ██ ███▀▀▀███ ███▄▄███ ███  ███▄ 
  ▀████▀████▀   ██▄ ██ ██ ███   ███ ▀██████▀ ████████▀ 
                                                       
                                                       
"""


def draw_banner():
    w = W()
    print_line(BR_CYAN + BOLD)
    for line in BANNER.strip("\n").split("\n"):
        pad = max(0, (w - len(line)) // 2)
        print_line(" " * pad + line)
    subtitle = f"  Windows System Optimizer  v{VERSION}  "
    pad = max(0, (w - len(subtitle)) // 2)
    print_line(" " * pad + BG_CYAN + BLACK + BOLD + subtitle + RESET)
    credit = f"by ricinus  •  github.com/ricinuss"
    pad = max(0, (w - len(credit)) // 2)
    print_line(RESET + DIM + " " * pad + credit + RESET)
    print_line()


# ──────────────────────────────────────────────────────────────────────────────
# Box drawing
# ──────────────────────────────────────────────────────────────────────────────

def draw_box(lines: list[str], title: str = "", color: str = CYAN, width: int = 0) -> str:
    """Return a double-line box string containing lines."""
    w = width or min(W() - 2, 78)
    inner = w - 2

    out = []
    if title:
        t = f"  {BOLD}{title}{RESET}{color}  "
        raw_len = len(title) + 4
        bar = BOX_H * ((inner - raw_len) // 2)
        out.append(color + BOX_TL + bar + t + bar + (BOX_H if (inner - raw_len) % 2 else "") + BOX_TR + RESET)
    else:
        out.append(color + BOX_TL + BOX_H * inner + BOX_TR + RESET)

    for line in lines:
        # Strip ANSI for length calc
        import re
        ansi_escape = re.compile(r'\x1B\[[0-9;]*m')
        raw_len = len(ansi_escape.sub("", line))
        pad = max(0, inner - raw_len - 2)
        out.append(color + BOX_V + RESET + " " + line + " " * pad + " " + color + BOX_V + RESET)

    out.append(color + BOX_BL + BOX_H * inner + BOX_BR + RESET)
    return "\n".join(out)


def draw_section_header(title: str, color: str = BR_CYAN):
    w = W()
    bar = TICK_H * (w - len(title) - 4)
    print_line(color + BOLD + f" {title} " + RESET + DIM + bar + RESET)


# ──────────────────────────────────────────────────────────────────────────────
# Progress Bar
# ──────────────────────────────────────────────────────────────────────────────

def make_progress_bar(pct: float, width: int = 30, fill_color: str = BR_GREEN, bg_color: str = DIM) -> str:
    pct    = max(0.0, min(100.0, pct))
    filled = int(width * pct / 100)
    empty  = width - filled

    if pct >= 80:
        fc = BR_RED
    elif pct >= 60:
        fc = BR_YELLOW
    else:
        fc = fill_color

    bar = fc + "█" * filled + bg_color + "░" * empty + RESET
    return f"[{bar}] {BOLD}{pct:5.1f}%{RESET}"


def draw_progress_bar_animated(label: str, pct: float, width: int = 32):
    bar = make_progress_bar(pct, width)
    sys.stdout.write(f"\r  {CYAN}{label:<24}{RESET} {bar}   ")
    sys.stdout.flush()


# ──────────────────────────────────────────────────────────────────────────────
# Score Badge
# ──────────────────────────────────────────────────────────────────────────────

def draw_score_badge(score: float, grade: str, grade_color: str):
    w = W()
    lines = [
        f"{BR_WHITE}System Health Score{RESET}",
        f"",
        f"  {grade_color}{BOLD}{'':>5}{score:.1f}%{RESET}",
        f"",
        f"  Grade:  {grade_color}{BOLD}{grade:^4}{RESET}",
    ]
    box = draw_box(lines, title="◆ HEALTH REPORT", color=grade_color, width=min(w - 4, 50))
    pad = max(0, (w - min(w - 4, 50)) // 2)
    for line in box.split("\n"):
        print_line(" " * pad + line)


# ──────────────────────────────────────────────────────────────────────────────
# Health Metric Row
# ──────────────────────────────────────────────────────────────────────────────

def draw_metric_row(label: str, value: str, score: float, bar_width: int = 20):
    color = BR_GREEN if score >= 80 else (BR_YELLOW if score >= 60 else BR_RED)
    bar   = make_progress_bar(score, bar_width, fill_color=color)
    print_line(f"  {color}{BOLD}{label:<18}{RESET}  {WHITE}{value}{RESET}")
    print_line(f"  {'':<18}  {bar}")


# ──────────────────────────────────────────────────────────────────────────────
# Spinner
# ──────────────────────────────────────────────────────────────────────────────

_SPINNER_FRAMES = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]


class Spinner:
    def __init__(self, label: str = "Working…", color: str = BR_CYAN):
        self.label   = label
        self.color   = color
        self._idx    = 0
        self._active = False
        self._thread = None

    def _spin(self):
        import threading
        while self._active:
            frame = _SPINNER_FRAMES[self._idx % len(_SPINNER_FRAMES)]
            sys.stdout.write(f"\r  {self.color}{frame}{RESET}  {self.label}  ")
            sys.stdout.flush()
            self._idx += 1
            time.sleep(0.08)

    def start(self):
        import threading
        self._active = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self, done_msg: str = ""):
        self._active = False
        if self._thread:
            self._thread.join()
        msg = done_msg or self.label
        sys.stdout.write(f"\r  {BR_GREEN}✔{RESET}  {msg}{' ' * 20}\n")
        sys.stdout.flush()


# ──────────────────────────────────────────────────────────────────────────────
# Checklist item
# ──────────────────────────────────────────────────────────────────────────────

def render_checklist_item(label: str, desc: str, selected: bool, focused: bool, risk: str = "safe") -> str:
    RISK_COLORS = {"safe": BR_GREEN, "balanced": BR_YELLOW, "extreme": BR_RED}
    rc = RISK_COLORS.get(risk, WHITE)

    check  = f"{BR_GREEN}✓{RESET}" if selected else f"{DIM}○{RESET}"
    cursor = f"{BR_CYAN}▶{RESET}" if focused  else "  "
    bg     = BG_CYAN + BLACK if focused else ""
    rs     = RESET if focused else ""

    risk_badge = f"{rc}[{risk.upper()[:3]}]{RESET}"
    return f" {cursor} {bg}[{check}{bg}] {BOLD}{label}{rs}{RESET}  {DIM}{desc[:45]}{RESET}  {risk_badge}"


# ──────────────────────────────────────────────────────────────────────────────
# Issue list
# ──────────────────────────────────────────────────────────────────────────────

def draw_issues(issues: list[str]):
    if not issues:
        print_line(f"  {BR_GREEN}✔  No issues detected{RESET}")
        return
    for iss in issues:
        print_line(f"  {BR_YELLOW}⚠  {WHITE}{iss}{RESET}")


# ──────────────────────────────────────────────────────────────────────────────
# Result summary
# ──────────────────────────────────────────────────────────────────────────────

def draw_apply_result(results):
    ok  = [r for r in results if r.success]
    bad = [r for r in results if not r.success]
    print_line()
    print_line(f"  {BR_GREEN}✔  {len(ok)} tweaks applied successfully{RESET}")
    if bad:
        print_line(f"  {BR_RED}✘  {len(bad)} tweaks had errors:{RESET}")
        for r in bad:
            print_line(f"     {DIM}{r.name}: {', '.join(r.errors)}{RESET}")
    print_line()
