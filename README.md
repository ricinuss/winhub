# WinHub 🚀
**Windows System Optimizer & Health Monitor**

A modern, CLI-based hub for Windows 10/11 system health diagnostics and optimizations. Written in Python, interacting with Windows internals via PowerShell and WMI. 

*Inspired by and adapted from the excellent Chris Titus WinUtil.*  
**Author:** ricinus ([@ricinuss](https://github.com/ricinuss))

---

## 🌟 Features

- **📊 System Health Diagnostics:** Live scanning of CPU, RAM, Disk, Startup impact, Background Services, and Power configurations to generate an instant health grade (A+ to F).
- **⚡ One-Click Optimization Presets:**
  - **Safe Mode:** Risk-free tweaks like telemetry removal and startup cleanup.
  - **Balanced Mode:** Moderate tweaks for daily use.
  - **Extreme Mode:** Aggressive performance tweaks for max speed.
- **🛠️ Custom Profile Builder:** Browse a detailed list of system tweaks, toggle them with `SPACE`, and build your own custom optimization profile.
- **💾 Profile Manager:** Save, load, export, and import `.json` tweaking profiles.
- **🤖 Headless Automation:** Ideal for IT technicians; apply a custom profile instantly via CLI without opening the UI menu.

## 🚀 Installation & Usage

### Method 1: The Quick Way (Web Installer)
Run WinHub directly from GitHub without downloading the repository manually. Open PowerShell as Administrator and run:
```powershell
iex (irm https://raw.githubusercontent.com/ricinuss/winhub/main/run.ps1)
```

### Method 2: Manual Download
1. **Clone or Download** the repository.
2. **Requirements:** Python 3.11+ (Make sure Python is added to your PATH).
3. **Run `winhub.bat`** (It will automatically request Administrator privileges and install the single dependency `colorama` if needed).

### Command-Line Arguments

WinHub can be fully automated from the command line:

```powershell
# Launch the interactive menu
winhub.bat

# Run a system health scan and print results to the console
winhub.bat --scan

# Apply a built-in preset non-interactively
winhub.bat --preset safe
winhub.bat --preset balanced

# Apply a custom exported JSON profile (great for fresh Windows installs)
winhub.bat --apply office_pc.json

# List all saved custom profiles
winhub.bat --list-profiles
```

## 📂 Project Structure

```text
winhub/
 ├── core/          # Constants, utilities, PowerShell runner, registry helpers
 ├── optimizers/    # Tweak applier engine, database of 18+ tweaks
 ├── profiles/      # Saved JSON optimization profiles
 ├── scanners/      # Health scanners (CPU, RAM, Disk, Services, Power)
 ├── ui/            # Terminal UI renderer, interactive menus
 ├── main.py        # CLI entry point
 └── winhub.bat     # Admin launcher & dependency checker
```

## 📜 Credits & Acknowledgments

- Huge thanks to **Chris Titus** and all contributors to [WinUtil](https://github.com/ChrisTitusTech/winutil) for curating, testing, and sharing the underlying registry and PowerShell tweaks that make this tool possible.
- Developed by **ricinus** ([GitHub](https://github.com/ricinuss)).

---
*Disclaimer: System tweaks involve modifying the Windows Registry and Services. While the "Safe" tweaks are heavily tested, always ensure you have a system restore point or backup before applying "Extreme" optimizations.*
