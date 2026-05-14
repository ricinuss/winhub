WinHub

Windows System Optimization and Diagnostics Toolkit

WinHub is a command-line utility for Windows 10 and Windows 11 focused on system diagnostics, performance optimization, and reusable deployment profiles. Built in Python, it integrates with native Windows components through PowerShell, WMI, and Registry APIs.

The project is inspired by WinUtil and adapts proven system tweaks into a streamlined CLI workflow.

Author: ricinus

Features
System Diagnostics

Analyze key system metrics and configuration states, including:

CPU usage and thermal behavior
Memory utilization
Disk health and performance
Startup applications
Background services
Power configuration

Based on collected data, WinHub generates an overall system health score.

Optimization Presets

WinHub includes three predefined optimization profiles:

Safe
Applies conservative tweaks intended for general stability, including startup cleanup and telemetry-related optimizations.

Balanced
Applies moderate performance and responsiveness improvements suitable for daily use.

Extreme
Applies aggressive system optimizations designed for maximum performance.

Custom Optimization Profiles

Create your own optimization profiles by selecting individual tweaks, then:

Save profiles locally
Export profiles as JSON
Import profiles across machines
Reuse profiles on fresh Windows installations
Automated Deployment

Profiles can be applied directly through the command line without opening the interactive interface, making WinHub suitable for system technicians, IT maintenance, and repeated deployments.

Installation
Quick Install (PowerShell)

Run directly from the repository:

iex (irm https://raw.githubusercontent.com/ricinuss/winhub/main/run.ps1)
Manual Installation
Clone or download the repository.
Install Python 3.11 or later.
Ensure Python is available in your system PATH.
Run:
winhub.bat

The launcher automatically requests administrator privileges and installs required dependencies when needed.

Command Line Usage

Launch interactive mode:

winhub.bat

Run a system diagnostic scan:

winhub.bat --scan

Apply a built-in optimization preset:

winhub.bat --preset safe
winhub.bat --preset balanced
winhub.bat --preset extreme

Apply a custom profile:

winhub.bat --apply office_pc.json

List saved profiles:

winhub.bat --list-profiles
Project Structure
winhub/
├── core/           Core utilities, PowerShell execution, registry helpers
├── optimizers/     Optimization engine and tweak definitions
├── profiles/       Saved optimization profiles
├── scanners/       Hardware and system diagnostics
├── ui/             Interactive terminal interface
├── main.py         CLI entry point
└── winhub.bat      Windows launcher
Credits

WinHub builds upon research and optimization work from the Chris Titus community project WinUtil.

Special thanks to all contributors involved in testing and documenting Windows optimization techniques.

Disclaimer

WinHub applies changes to system settings, services, and the Windows Registry. Before applying performance tweaks, especially under the Extreme preset, it is strongly recommended to create a restore point or full system backup.
