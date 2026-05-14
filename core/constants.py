# ============================================================
# WinHub — Core Constants
# Author credit: ricinus (https://github.com/ricinuss)
# Inspired by Chris Titus WinUtil
# ============================================================

VERSION = "1.0.0"
APP_NAME = "WinHub"
APP_SUBTITLE = "Windows System Optimizer & Health Monitor"
AUTHOR = "ricinus"
AUTHOR_URL = "https://github.com/ricinuss"

# ANSI escape codes
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
BLINK   = "\033[5m"

# Foreground colors
BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

# Bright foreground
BR_RED     = "\033[91m"
BR_GREEN   = "\033[92m"
BR_YELLOW  = "\033[93m"
BR_BLUE    = "\033[94m"
BR_MAGENTA = "\033[95m"
BR_CYAN    = "\033[96m"
BR_WHITE   = "\033[97m"

# Background colors
BG_BLACK   = "\033[40m"
BG_BLUE    = "\033[44m"
BG_CYAN    = "\033[46m"
BG_WHITE   = "\033[47m"
BG_MAGENTA = "\033[45m"

# Box drawing
BOX_TL  = "╔"
BOX_TR  = "╗"
BOX_BL  = "╚"
BOX_BR  = "╝"
BOX_H   = "═"
BOX_V   = "║"
BOX_ML  = "╠"
BOX_MR  = "╣"
BOX_T   = "╦"
BOX_B   = "╩"
BOX_X   = "╬"

TICK_TL = "┌"
TICK_TR = "┐"
TICK_BL = "└"
TICK_BR = "┘"
TICK_H  = "─"
TICK_V  = "│"
TICK_ML = "├"
TICK_MR = "┤"

# Score/grade thresholds
SCORE_GRADE = {
    (90, 101): ("A+", BR_GREEN),
    (80, 90):  ("A",  BR_GREEN),
    (70, 80):  ("B",  BR_YELLOW),
    (60, 70):  ("C",  YELLOW),
    (50, 60):  ("D",  BR_RED),
    (0,  50):  ("F",  RED),
}

# Profile names
PROFILES_DIR = "profiles"

# Key codes (Windows)
KEY_UP    = 72
KEY_DOWN  = 80
KEY_LEFT  = 75
KEY_RIGHT = 77
KEY_ENTER = 13
KEY_SPACE = 32
KEY_ESC   = 27
KEY_BACK  = 8
