"""
WinHub — CPU Scanner
Author: ricinus (https://github.com/ricinuss)
"""
import time
from core.utils import run_powershell, clamp


def scan_cpu() -> dict:
    """
    Returns CPU metrics dict:
      name, cores, threads, speed_ghz, usage_pct, score (0-100), issues
    """
    result = {
        "name":       "Unknown CPU",
        "cores":      0,
        "threads":    0,
        "speed_ghz":  0.0,
        "max_speed_ghz": 0.0,
        "usage_pct":  0.0,
        "score":      50,
        "issues":     [],
        "raw":        {},
    }

    script = r"""
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$load = (Get-CimInstance Win32_Processor).LoadPercentage
$json = @{
    Name        = $cpu.Name.Trim()
    Cores       = $cpu.NumberOfCores
    Threads     = $cpu.NumberOfLogicalProcessors
    SpeedMHz    = $cpu.CurrentClockSpeed
    MaxSpeedMHz = $cpu.MaxClockSpeed
    LoadPct     = $load
} | ConvertTo-Json -Compress
Write-Output $json
"""
    rc, stdout, _ = run_powershell(script)
    if rc == 0 and stdout:
        import json
        try:
            data = json.loads(stdout)
            result["name"]          = data.get("Name", "Unknown")
            result["cores"]         = int(data.get("Cores", 0))
            result["threads"]       = int(data.get("Threads", 0))
            result["speed_ghz"]     = round(data.get("SpeedMHz", 0) / 1000, 2)
            result["max_speed_ghz"] = round(data.get("MaxSpeedMHz", 0) / 1000, 2)
            result["usage_pct"]     = float(data.get("LoadPct", 0))
            result["raw"]           = data
        except Exception:
            pass

    # Score calculation
    score = 100
    issues = []

    usage = result["usage_pct"]
    if usage >= 90:
        score -= 40
        issues.append(f"CPU critically overloaded ({usage:.0f}%)")
    elif usage >= 70:
        score -= 20
        issues.append(f"CPU heavily loaded ({usage:.0f}%)")
    elif usage >= 50:
        score -= 10
        issues.append(f"CPU moderately loaded ({usage:.0f}%)")

    max_spd = result["max_speed_ghz"]
    cur_spd = result["speed_ghz"]
    if max_spd > 0 and cur_spd < max_spd * 0.6:
        score -= 15
        issues.append(f"CPU throttled ({cur_spd:.1f}/{max_spd:.1f} GHz)")

    if result["cores"] == 0:
        score -= 10

    result["score"]  = clamp(score, 0, 100)
    result["issues"] = issues
    return result
