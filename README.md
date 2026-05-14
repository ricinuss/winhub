# WinHub

**Windows System Optimizer & Health Monitor**

A CLI-based tool for Windows 10/11 system diagnostics and optimization. Written in Python, interfacing with Windows internals via PowerShell and WMI.

*Inspired by and adapted from Chris Titus' [WinUtil](https://github.com/ChrisTitusTech/winutil).*

**Author:** ricinus — [@ricinuss](https://github.com/ricinuss)

---

## Features

**System Health Diagnostics**
Live scanning of CPU, RAM, disk, startup impact, background services, and power configuration to produce an instant health grade (A+ to F).

**Optimization Presets**
- *Safe* — Risk-free tweaks: telemetry removal, startup cleanup.
- *Balanced* — Moderate adjustments for everyday use.
- *Extreme* — Aggressive performance tuning for maximum throughput.

**Custom Profile Builder**
Browse the full list of available tweaks, toggle individual items with `Space`, and save the result as a reusable profile.

**Profile Manager**
Save, load, export, and import optimization profiles as `.json` files.

**Headless / CLI Automation**
Apply any profile non-interactively from the command line — useful for scripted deployments and fresh Windows installs.

---

## Installation

### Option 1 — Web installer

Run directly from GitHub without cloning the repository. Open PowerShell as Administrator:

```powershell
iex (irm https://raw.githubusercontent.com/ricinuss/winhub/main/run.ps1)
```

### Option 2 — Manual

1. Clone or download the repository.
2. Install **Python 3.11+** and ensure it is on your `PATH`.
3. Run `winhub.bat` — it requests Administrator privileges automatically and installs `colorama` if needed.

---

## Usage

```powershell
# Launch the interactive menu
winhub.bat

# Run a health scan and print results
winhub.bat --scan

# Apply a built-in preset non-interactively
winhub.bat --preset safe
winhub.bat --preset balanced

# Apply a saved JSON profile
winhub.bat --apply office_pc.json

# List all saved profiles
winhub.bat --list-profiles
```

---

## Project Structure
winhub/
├── core/          # Constants, utilities, PowerShell runner, registry helpers
├── optimizers/    # Tweak engine and database (18+ tweaks)
├── profiles/      # Saved JSON optimization profiles
├── scanners/      # Health scanners: CPU, RAM, disk, services, power
├── ui/            # Terminal renderer and interactive menus
├── main.py        # CLI entry point
└── winhub.bat     # Admin launcher and dependency checker

---

## Credits

Thanks to **Chris Titus** and the [WinUtil](https://github.com/ChrisTitusTech/winutil) contributors for curating and testing the registry and PowerShell tweaks that underpin this tool.

---

*System tweaks modify the Windows Registry and service configuration. Safe-mode tweaks are well-tested, but it is recommended to create a restore point before applying Balanced or Extreme presets.*
