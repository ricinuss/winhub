"""
WinHub — Tweaks Database
All registry/service/script tweaks, adapted from Chris Titus WinUtil tweaks.json
Author: ricinus (https://github.com/ricinuss)
"""

# Each tweak entry:
#   id       : unique key
#   name     : display name
#   desc     : short description
#   category : tag for grouping/profiles
#   risk     : "safe" | "balanced" | "extreme"
#   registry : list of {path, name, value, type, original}
#   service  : list of {name, startup_type, original_type}
#   script   : PowerShell string to invoke
#   undo     : PowerShell string to undo

TWEAKS = [
    # ── TELEMETRY ──────────────────────────────────────────────────────────
    {
        "id":       "disable_telemetry",
        "name":     "Disable Telemetry",
        "desc":     "Stops Microsoft telemetry services and data collection.",
        "category": "privacy",
        "risk":     "safe",
        "registry": [
            {"path": "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection",
             "name": "AllowTelemetry", "value": 0, "type": "DWord", "original": 1},
            {"path": "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo",
             "name": "Enabled", "value": 0, "type": "DWord", "original": 1},
            {"path": "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Privacy",
             "name": "TailoredExperiencesWithDiagnosticDataEnabled", "value": 0, "type": "DWord", "original": 1},
            {"path": "HKCU:\\Software\\Microsoft\\Siuf\\Rules",
             "name": "NumberOfSIUFInPeriod", "value": 0, "type": "DWord", "original": 3},
            {"path": "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System",
             "name": "PublishUserActivities", "value": 0, "type": "DWord", "original": 1},
        ],
        "service": [
            {"name": "DiagTrack",   "startup_type": "Disabled", "original_type": "Automatic"},
            {"name": "dmwappushservice", "startup_type": "Disabled", "original_type": "Manual"},
        ],
        "script": "Set-MpPreference -SubmitSamplesConsent 2; Set-Service -Name diagtrack -StartupType Disabled; Set-Service -Name wermgr -StartupType Disabled",
        "undo":   "Set-MpPreference -SubmitSamplesConsent 1; Set-Service -Name diagtrack -StartupType Automatic; Set-Service -Name wermgr -StartupType Automatic",
    },

    # ── ACTIVITY HISTORY ───────────────────────────────────────────────────
    {
        "id":       "disable_activity_history",
        "name":     "Disable Activity History",
        "desc":     "Clears and disables Windows activity tracking.",
        "category": "privacy",
        "risk":     "safe",
        "registry": [
            {"path": "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System",
             "name": "EnableActivityFeed", "value": 0, "type": "DWord", "original": 1},
            {"path": "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System",
             "name": "PublishUserActivities", "value": 0, "type": "DWord", "original": 1},
            {"path": "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System",
             "name": "UploadUserActivities", "value": 0, "type": "DWord", "original": 1},
        ],
        "service": [],
        "script": "",
        "undo":   "",
    },

    # ── CONSUMER FEATURES ──────────────────────────────────────────────────
    {
        "id":       "disable_consumer_features",
        "name":     "Disable Consumer Features",
        "desc":     "Prevents Windows from auto-installing Store bloat apps.",
        "category": "privacy",
        "risk":     "safe",
        "registry": [
            {"path": "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\CloudContent",
             "name": "DisableWindowsConsumerFeatures", "value": 1, "type": "DWord", "original": 0},
        ],
        "service": [],
        "script": "",
        "undo":   "",
    },

    # ── LOCATION ───────────────────────────────────────────────────────────
    {
        "id":       "disable_location",
        "name":     "Disable Location Tracking",
        "desc":     "Disables geolocation service and registry entries.",
        "category": "privacy",
        "risk":     "safe",
        "registry": [
            {"path": "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location",
             "name": "Value", "value": "Deny", "type": "String", "original": "Allow"},
            {"path": "HKLM:\\SYSTEM\\Maps",
             "name": "AutoUpdateEnabled", "value": 0, "type": "DWord", "original": 1},
        ],
        "service": [
            {"name": "lfsvc", "startup_type": "Disabled", "original_type": "Manual"},
        ],
        "script": "",
        "undo":   "",
    },

    # ── SERVICES SET TO MANUAL ─────────────────────────────────────────────
    {
        "id":       "services_to_manual",
        "name":     "Optimize Service Startup",
        "desc":     "Sets unnecessary auto-services to Manual. Reduces svchost bloat.",
        "category": "performance",
        "risk":     "safe",
        "registry": [],
        "service": [
            {"name": "CscService",    "startup_type": "Disabled", "original_type": "Manual"},
            {"name": "MapsBroker",    "startup_type": "Manual",   "original_type": "Automatic"},
            {"name": "StorSvc",       "startup_type": "Manual",   "original_type": "Automatic"},
            {"name": "SharedAccess",  "startup_type": "Disabled", "original_type": "Automatic"},
            {"name": "TrkWks",        "startup_type": "Disabled", "original_type": "Automatic"},
            {"name": "RemoteRegistry","startup_type": "Disabled", "original_type": "Manual"},
            {"name": "Fax",           "startup_type": "Disabled", "original_type": "Manual"},
        ],
        "script": r"""
$Memory = (Get-CimInstance Win32_PhysicalMemory | Measure-Object Capacity -Sum).Sum / 1KB
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control" -Name SvcHostSplitThresholdInKB -Value $Memory
""",
        "undo":   "",
    },

    # ── HIBERNATE ──────────────────────────────────────────────────────────
    {
        "id":       "disable_hibernation",
        "name":     "Disable Hibernation",
        "desc":     "Frees up disk space used by hiberfil.sys (not needed on desktops).",
        "category": "performance",
        "risk":     "safe",
        "registry": [
            {"path": "HKLM:\\System\\CurrentControlSet\\Control\\Session Manager\\Power",
             "name": "HibernateEnabled", "value": 0, "type": "DWord", "original": 1},
        ],
        "service": [],
        "script": "powercfg.exe /hibernate off",
        "undo":   "powercfg.exe /hibernate on",
    },

    # ── VISUAL EFFECTS ─────────────────────────────────────────────────────
    {
        "id":       "performance_visual_effects",
        "name":     "Visual Effects → Best Performance",
        "desc":     "Disables animations, shadows, and Aero Peek for raw speed.",
        "category": "performance",
        "risk":     "balanced",
        "registry": [
            {"path": "HKCU:\\Control Panel\\Desktop",
             "name": "DragFullWindows", "value": "0", "type": "String", "original": "1"},
            {"path": "HKCU:\\Control Panel\\Desktop",
             "name": "MenuShowDelay", "value": "200", "type": "String", "original": "400"},
            {"path": "HKCU:\\Control Panel\\Desktop\\WindowMetrics",
             "name": "MinAnimate", "value": "0", "type": "String", "original": "1"},
            {"path": "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
             "name": "ListviewAlphaSelect", "value": 0, "type": "DWord", "original": 1},
            {"path": "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
             "name": "ListviewShadow", "value": 0, "type": "DWord", "original": 1},
            {"path": "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
             "name": "TaskbarAnimations", "value": 0, "type": "DWord", "original": 1},
            {"path": "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects",
             "name": "VisualFXSetting", "value": 3, "type": "DWord", "original": 1},
            {"path": "HKCU:\\Software\\Microsoft\\Windows\\DWM",
             "name": "EnableAeroPeek", "value": 0, "type": "DWord", "original": 1},
        ],
        "service": [],
        "script": 'Set-ItemProperty -Path "HKCU:\\Control Panel\\Desktop" -Name "UserPreferencesMask" -Type Binary -Value ([byte[]](144,18,3,128,16,0,0,0))',
        "undo":   'Remove-ItemProperty -Path "HKCU:\\Control Panel\\Desktop" -Name "UserPreferencesMask" -ErrorAction SilentlyContinue',
    },

    # ── HIGH PERFORMANCE POWER ─────────────────────────────────────────────
    {
        "id":       "power_high_performance",
        "name":     "Power Plan → High Performance",
        "desc":     "Switches to High Performance power plan for max CPU speed.",
        "category": "performance",
        "risk":     "balanced",
        "registry": [],
        "service": [],
        "script": "powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
        "undo":   "powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e",
    },

    # ── ULTIMATE PERFORMANCE ───────────────────────────────────────────────
    {
        "id":       "power_ultimate_performance",
        "name":     "Power Plan → Ultimate Performance",
        "desc":     "Enables the hidden Ultimate Performance plan. Maximum throughput.",
        "category": "performance",
        "risk":     "extreme",
        "registry": [],
        "service": [],
        "script": r"""
$guid = "e9a42b02-d5df-448d-aa00-03f14749eb61"
powercfg /duplicatescheme $guid 2>$null
powercfg /setactive $guid
""",
        "undo":   "powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e",
    },

    # ── STARTUP CLEANUP ────────────────────────────────────────────────────
    {
        "id":       "startup_cleanup",
        "name":     "Startup Cleanup",
        "desc":     "Disables known slow/unnecessary startup programs via registry.",
        "category": "performance",
        "risk":     "safe",
        "registry": [],
        "service": [],
        "script": r"""
$keys = @(
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run"
)
$bloat = @("OneDrive","Spotify","Discord","Teams","Cortana","BingWeather","Skype","EpicGames")
foreach ($key in $keys) {
    if (Test-Path $key) {
        $vals = Get-ItemProperty $key -ErrorAction SilentlyContinue
        foreach ($b in $bloat) {
            $prop = $vals.PSObject.Properties | Where-Object { $_.Name -like "*$b*" }
            if ($prop) {
                Remove-ItemProperty -Path $key -Name $prop.Name -ErrorAction SilentlyContinue
                Write-Host "Removed startup: $($prop.Name)"
            }
        }
    }
}
""",
        "undo":   "",
    },

    # ── NETWORK OPTIMIZATION ───────────────────────────────────────────────
    {
        "id":       "network_optimization",
        "name":     "Network Optimization",
        "desc":     "Disables Nagle algorithm, sets DNS cache, tunes TCP parameters.",
        "category": "network",
        "risk":     "balanced",
        "registry": [
            {"path": "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters",
             "name": "TcpAckFrequency", "value": 1, "type": "DWord", "original": 2},
            {"path": "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters",
             "name": "TCPNoDelay", "value": 1, "type": "DWord", "original": 0},
            {"path": "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters",
             "name": "TcpDelAckTicks", "value": 0, "type": "DWord", "original": 2},
            {"path": "HKLM:\\SOFTWARE\\Microsoft\\MSMQ\\Parameters",
             "name": "TCPNoDelay", "value": 1, "type": "DWord", "original": 0},
        ],
        "service": [],
        "script": r"""
netsh int tcp set global autotuninglevel=normal
netsh int tcp set global chimney=enabled
netsh int tcp set global dca=enabled
netsh int tcp set global netdma=enabled
netsh int tcp set global ecncapability=enabled
ipconfig /flushdns
""",
        "undo":   "netsh int tcp set global autotuninglevel=normal",
    },

    # ── GAMING TWEAKS ──────────────────────────────────────────────────────
    {
        "id":       "gaming_tweaks",
        "name":     "Gaming Tweaks",
        "desc":     "Enables Game Mode, disables Xbox Game Bar, sets GPU scheduling.",
        "category": "gaming",
        "risk":     "balanced",
        "registry": [
            {"path": "HKCU:\\Software\\Microsoft\\GameBar",
             "name": "AllowAutoGameMode", "value": 1, "type": "DWord", "original": 0},
            {"path": "HKCU:\\Software\\Microsoft\\GameBar",
             "name": "AutoGameModeEnabled", "value": 1, "type": "DWord", "original": 0},
            {"path": "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR",
             "name": "AppCaptureEnabled", "value": 0, "type": "DWord", "original": 1},
            {"path": "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games",
             "name": "GPU Priority", "value": 8, "type": "DWord", "original": 2},
            {"path": "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games",
             "name": "Priority", "value": 6, "type": "DWord", "original": 2},
            {"path": "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games",
             "name": "Scheduling Category", "value": "High", "type": "String", "original": "Medium"},
            {"path": "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers",
             "name": "HwSchMode", "value": 2, "type": "DWord", "original": 1},
        ],
        "service": [
            {"name": "XblAuthManager", "startup_type": "Disabled", "original_type": "Manual"},
            {"name": "XblGameSave",    "startup_type": "Disabled", "original_type": "Manual"},
            {"name": "XboxNetApiSvc",  "startup_type": "Disabled", "original_type": "Manual"},
        ],
        "script": "",
        "undo":   "",
    },

    # ── DEBLOAT APPX ───────────────────────────────────────────────────────
    {
        "id":       "debloat_appx",
        "name":     "Remove Bloatware Apps",
        "desc":     "Removes pre-installed Microsoft apps most users don't want.",
        "category": "debloat",
        "risk":     "balanced",
        "registry": [],
        "service": [],
        "script": r"""
$apps = @(
    "Microsoft.BingNews","Microsoft.BingWeather","Microsoft.GetHelp",
    "Microsoft.MicrosoftSolitaireCollection","Microsoft.WindowsFeedbackHub",
    "Microsoft.ZuneMusic","MicrosoftCorporationII.QuickAssist",
    "Microsoft.PowerAutomateDesktop","Microsoft.Todos","Clipchamp.Clipchamp",
    "Microsoft.OutlookForWindows","Microsoft.WindowsAlarms"
)
foreach ($app in $apps) {
    $pkg = Get-AppxPackage -Name $app -AllUsers -ErrorAction SilentlyContinue
    if ($pkg) {
        $pkg | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue
        Write-Host "Removed: $app"
    }
}
""",
        "undo":   "",
    },

    # ── DISABLE WINDOWS AI ─────────────────────────────────────────────────
    {
        "id":       "disable_windows_ai",
        "name":     "Disable Windows AI / Copilot",
        "desc":     "Removes Copilot and disables AI features (Recall, etc.).",
        "category": "privacy",
        "risk":     "balanced",
        "registry": [
            {"path": "HKLM:\\SOFTWARE\\Policies\\WindowsNotepad",
             "name": "DisableAIFeatures", "value": 1, "type": "DWord", "original": 0},
            {"path": "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer",
             "name": "SettingsPageVisibility", "value": "hide:aicomponents", "type": "String", "original": ""},
        ],
        "service": [
            {"name": "WSAIFabricSvc", "startup_type": "Disabled", "original_type": "Automatic"},
        ],
        "script": "Get-AppxPackage -AllUsers *Copilot* | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue",
        "undo":   "",
    },

    # ── DISABLE SUPERFETCH / SYSMAIN ──────────────────────────────────────
    {
        "id":       "disable_sysmain",
        "name":     "Disable SysMain (Superfetch)",
        "desc":     "Stops Superfetch which can thrash HDDs. Usually OK to disable on SSD.",
        "category": "performance",
        "risk":     "extreme",
        "registry": [],
        "service": [
            {"name": "SysMain", "startup_type": "Disabled", "original_type": "Automatic"},
        ],
        "script": "",
        "undo":   "",
    },

    # ── RIGHT CLICK MENU ───────────────────────────────────────────────────
    {
        "id":       "classic_right_click",
        "name":     "Restore Classic Right-Click Menu",
        "desc":     "Brings back the full Windows 10 context menu in Windows 11.",
        "category": "ui",
        "risk":     "safe",
        "registry": [],
        "service": [],
        "script": r"""
New-Item -Path "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" -Name "InprocServer32" -Force -Value "" | Out-Null
Stop-Process -Name "explorer" -Force -ErrorAction SilentlyContinue
""",
        "undo":   r"""
Remove-Item -Path "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" -Recurse -Force -ErrorAction SilentlyContinue
Stop-Process -Name "explorer" -Force -ErrorAction SilentlyContinue
""",
    },

    # ── POWERSHELL 7 TELEMETRY ─────────────────────────────────────────────
    {
        "id":       "disable_ps7_telemetry",
        "name":     "Disable PowerShell 7 Telemetry",
        "desc":     "Sets POWERSHELL_TELEMETRY_OPTOUT=1 system-wide.",
        "category": "privacy",
        "risk":     "safe",
        "registry": [],
        "service": [],
        "script": "[Environment]::SetEnvironmentVariable('POWERSHELL_TELEMETRY_OPTOUT', '1', 'Machine')",
        "undo":   "[Environment]::SetEnvironmentVariable('POWERSHELL_TELEMETRY_OPTOUT', '', 'Machine')",
    },

    # ── WPBT DISABLE ──────────────────────────────────────────────────────
    {
        "id":       "disable_wpbt",
        "name":     "Disable WPBT (Vendor Boot Execution)",
        "desc":     "Prevents OEM vendor programs from running at boot via ACPI table.",
        "category": "security",
        "risk":     "safe",
        "registry": [
            {"path": "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager",
             "name": "DisableWpbtExecution", "value": 1, "type": "DWord", "original": 0},
        ],
        "service": [],
        "script": "",
        "undo":   "",
    },

    # ── DISK CLEANUP ──────────────────────────────────────────────────────
    {
        "id":       "disk_cleanup",
        "name":     "Run Disk Cleanup",
        "desc":     "Cleans temp files and old Windows Update cache on drive C:.",
        "category": "maintenance",
        "risk":     "safe",
        "registry": [],
        "service": [],
        "script": r"""
cleanmgr.exe /d C: /VERYLOWDISK /autoclean
$updateCleanupKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Update Cleanup"
if (Test-Path $updateCleanupKey) {
    Set-ItemProperty -Path $updateCleanupKey -Name StateFlags0001 -Value 2 -Type DWord
    Start-Process cleanmgr.exe -ArgumentList "/sagerun:1" -Wait
}
Write-Host "Disk cleanup complete."
""",
        "undo":   "",
    },

    # ── DNS CACHE OPTIMIZATION ────────────────────────────────────────────
    {
        "id":       "dns_cache_optimize",
        "name":     "Optimize DNS Cache Settings",
        "desc":     "Increases DNS cache size for faster hostname resolution.",
        "category": "network",
        "risk":     "safe",
        "registry": [
            {"path": "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Dnscache\\Parameters",
             "name": "MaxCacheEntryTtlLimit", "value": 86400, "type": "DWord", "original": 86400},
            {"path": "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Dnscache\\Parameters",
             "name": "CacheHashTableBucketSize", "value": 1, "type": "DWord", "original": 1},
            {"path": "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Dnscache\\Parameters",
             "name": "CacheHashTableSize", "value": 384, "type": "DWord", "original": 128},
            {"path": "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Dnscache\\Parameters",
             "name": "MaxCacheSize", "value": 65536, "type": "DWord", "original": 4096},
        ],
        "service": [],
        "script": "ipconfig /flushdns",
        "undo":   "",
    },
]

# ── Profile preset → list of tweak IDs ────────────────────────────────────

PRESET_SAFE = [
    "disable_telemetry",
    "disable_activity_history",
    "disable_consumer_features",
    "disable_location",
    "services_to_manual",
    "disable_hibernation",
    "startup_cleanup",
    "disk_cleanup",
    "disable_ps7_telemetry",
    "disable_wpbt",
    "dns_cache_optimize",
]

PRESET_BALANCED = PRESET_SAFE + [
    "performance_visual_effects",
    "power_high_performance",
    "network_optimization",
    "debloat_appx",
    "disable_windows_ai",
    "classic_right_click",
]

PRESET_EXTREME = PRESET_BALANCED + [
    "power_ultimate_performance",
    "disable_sysmain",
    "gaming_tweaks",
]

PRESET_GAMING = [
    "disable_telemetry",
    "services_to_manual",
    "disable_hibernation",
    "performance_visual_effects",
    "power_ultimate_performance",
    "gaming_tweaks",
    "network_optimization",
    "startup_cleanup",
    "disk_cleanup",
]


def get_tweak_by_id(tweak_id: str) -> dict | None:
    for t in TWEAKS:
        if t["id"] == tweak_id:
            return t
    return None


def get_tweaks_by_ids(ids: list) -> list:
    return [t for t in TWEAKS if t["id"] in ids]
