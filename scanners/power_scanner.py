"""
WinHub — Power & Temperature Scanner
Author: ricinus (https://github.com/ricinuss)
"""
from core.utils import run_powershell, clamp


def scan_power() -> dict:
    result = {
        "plan_name":     "Unknown",
        "plan_guid":     "",
        "is_balanced":   False,
        "is_high_perf":  False,
        "is_power_save": False,
        "battery_pct":   -1,   # -1 = desktop (no battery)
        "plugged_in":    True,
        "score":         100,
        "issues":        [],
    }

    script = r"""
$plan = powercfg /getactivescheme 2>$null
$battery = Get-CimInstance -ClassName Win32_Battery -ErrorAction SilentlyContinue
$charge = if ($battery) { $battery.EstimatedChargeRemaining } else { -1 }
$plugged = if ($battery) { $battery.BatteryStatus -eq 2 } else { $true }
@{
    PlanLine  = $plan
    ChargePct = $charge
    PluggedIn = $plugged
} | ConvertTo-Json -Compress
"""
    rc, stdout, _ = run_powershell(script)
    if rc == 0 and stdout:
        import json, re
        try:
            data = json.loads(stdout)
            plan_line = str(data.get("PlanLine", ""))
            # Extract GUID and name from powercfg output
            m = re.search(r"\((.+?)\)\s*$", plan_line)
            if m:
                result["plan_name"] = m.group(1).strip()
            m2 = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", plan_line, re.I)
            if m2:
                result["plan_guid"] = m2.group(1).lower()

            name_lower = result["plan_name"].lower()
            result["is_high_perf"]  = "high" in name_lower or "ultimate" in name_lower
            result["is_balanced"]   = "balanced" in name_lower
            result["is_power_save"] = "saver" in name_lower or "saving" in name_lower

            batt = data.get("ChargePct")
            result["battery_pct"]  = int(batt) if batt is not None and batt != -1 else -1
            result["plugged_in"]   = bool(data.get("PluggedIn", True))
        except Exception:
            pass

    score  = 100
    issues = []

    if result["is_power_save"]:
        score -= 20
        issues.append(f"Power Saver plan active — hurts performance")
    elif result["is_balanced"]:
        score -= 10
        issues.append("Balanced power plan — not optimal for performance")

    batt = result["battery_pct"]
    if 0 <= batt < 20 and not result["plugged_in"]:
        score -= 15
        issues.append(f"Battery low ({batt}%) and unplugged")

    result["score"]  = clamp(score, 0, 100)
    result["issues"] = issues
    return result


def scan_temperature() -> dict:
    result = {
        "cpu_temp_c":  -1,
        "available":   False,
        "score":       100,
        "issues":      [],
    }

    # Try OpenHardwareMonitor WMI namespace (if installed)
    script = r"""
try {
    $temp = Get-CimInstance -Namespace root/OpenHardwareMonitor -ClassName Sensor -ErrorAction Stop |
            Where-Object { $_.SensorType -eq 'Temperature' -and $_.Name -like '*CPU*' } |
            Select-Object -First 1 -ExpandProperty Value
    if ($temp) { Write-Output $temp } else { Write-Output -1 }
} catch {
    # Try MSAcpi_ThermalZoneTemperature
    try {
        $tz = Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction Stop |
              Select-Object -First 1
        $tempC = [math]::Round(($tz.CurrentTemperature - 2732) / 10.0, 1)
        Write-Output $tempC
    } catch {
        Write-Output -1
    }
}
"""
    rc, stdout, _ = run_powershell(script)
    if rc == 0 and stdout.strip():
        try:
            temp = float(stdout.strip())
            if temp > 0:
                result["cpu_temp_c"] = temp
                result["available"]  = True
        except Exception:
            pass

    score  = 100
    issues = []
    temp   = result["cpu_temp_c"]

    if result["available"]:
        if temp >= 95:
            score -= 40
            issues.append(f"CPU critically hot ({temp:.0f}°C) — check cooling!")
        elif temp >= 85:
            score -= 25
            issues.append(f"CPU running very hot ({temp:.0f}°C)")
        elif temp >= 75:
            score -= 10
            issues.append(f"CPU temperature elevated ({temp:.0f}°C)")
    else:
        # Can't read temp → neutral penalty, just note it
        issues.append("Temperature sensor unavailable (install OpenHardwareMonitor for readings)")

    result["score"]  = clamp(score, 0, 100)
    result["issues"] = issues
    return result
