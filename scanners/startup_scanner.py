"""
WinHub — Startup Impact Scanner
Author: ricinus (https://github.com/ricinuss)
"""
from core.utils import run_powershell, clamp


def scan_startup() -> dict:
    result = {
        "entries":      [],
        "total":        0,
        "high_impact":  0,
        "score":        100,
        "issues":       [],
    }

    script = r"""
$items = Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location
$items | ForEach-Object {
    [PSCustomObject]@{
        Name     = $_.Name
        Command  = $_.Command
        Location = $_.Location
    }
} | ConvertTo-Json -Compress -Depth 2
"""
    rc, stdout, _ = run_powershell(script)
    entries = []
    if rc == 0 and stdout and stdout not in ("null", ""):
        import json
        try:
            raw = json.loads(stdout)
            if isinstance(raw, dict):
                raw = [raw]
            for item in raw:
                name = str(item.get("Name", "Unknown"))
                cmd  = str(item.get("Command", ""))
                loc  = str(item.get("Location", ""))
                entries.append({"name": name, "command": cmd, "location": loc})
        except Exception:
            pass

    result["entries"] = entries
    result["total"]   = len(entries)

    score  = 100
    issues = []

    if len(entries) > 25:
        score -= 30
        issues.append(f"{len(entries)} startup entries (very high)")
    elif len(entries) > 15:
        score -= 15
        issues.append(f"{len(entries)} startup entries (high)")
    elif len(entries) > 8:
        score -= 5
        issues.append(f"{len(entries)} startup entries (moderate)")

    result["score"]  = clamp(score, 0, 100)
    result["issues"] = issues
    return result
