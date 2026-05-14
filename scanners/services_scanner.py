"""
WinHub — Services Scanner
Author: ricinus (https://github.com/ricinuss)
"""
from core.utils import run_powershell, clamp

# Services known to be bloat/telemetry — adapted from WinUtil tweaks.json
BLOAT_SERVICES = {
    "DiagTrack",       # Connected User Experiences and Telemetry
    "dmwappushservice",# WAP Push Message Routing Service
    "SysMain",         # Superfetch (can hurt SSD perf)
    "WSearch",         # Windows Search indexer
    "XblAuthManager",  # Xbox Live Auth Manager
    "XblGameSave",     # Xbox Live Game Save Service
    "XboxNetApiSvc",   # Xbox Live Networking Service
    "MapsBroker",      # Downloaded Maps Manager
    "lfsvc",           # Geolocation Service
    "SharedAccess",    # Internet Connection Sharing
    "RemoteRegistry",  # Remote Registry
    "Fax",             # Fax
    "TrkWks",          # Distributed Link Tracking Client
}


def scan_services() -> dict:
    result = {
        "total_running":  0,
        "bloat_running":  [],
        "auto_services":  0,
        "score":          100,
        "issues":         [],
    }

    script = r"""
Get-Service | Where-Object { $_.Status -eq 'Running' } | Select-Object Name, DisplayName, StartType |
    ConvertTo-Json -Compress -Depth 2
"""
    rc, stdout, _ = run_powershell(script)
    running = []
    if rc == 0 and stdout and stdout not in ("null", ""):
        import json
        try:
            raw = json.loads(stdout)
            if isinstance(raw, dict):
                raw = [raw]
            running = raw
        except Exception:
            pass

    result["total_running"] = len(running)

    bloat_found = []
    auto_count  = 0
    for svc in running:
        name = svc.get("Name", "")
        if name in BLOAT_SERVICES:
            bloat_found.append(name)
        if str(svc.get("StartType", "")).lower() == "automatic":
            auto_count += 1

    result["bloat_running"] = bloat_found
    result["auto_services"] = auto_count

    score  = 100
    issues = []

    if len(bloat_found) >= 5:
        score -= 25
        issues.append(f"{len(bloat_found)} bloat/telemetry services running")
    elif len(bloat_found) >= 2:
        score -= 10
        issues.append(f"{len(bloat_found)} bloat services still active")

    if len(running) > 120:
        score -= 15
        issues.append(f"Excessive services running ({len(running)})")
    elif len(running) > 80:
        score -= 5
        issues.append(f"High service count ({len(running)})")

    result["score"]  = clamp(score, 0, 100)
    result["issues"] = issues
    return result
