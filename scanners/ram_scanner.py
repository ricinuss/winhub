"""
WinHub — RAM Scanner
Author: ricinus (https://github.com/ricinuss)
"""
from core.utils import run_powershell, clamp, format_bytes


def scan_ram() -> dict:
    result = {
        "total_gb":    0.0,
        "used_gb":     0.0,
        "free_gb":     0.0,
        "usage_pct":   0.0,
        "speed_mhz":   0,
        "slots_used":  0,
        "slots_total": 0,
        "type":        "Unknown",
        "score":       50,
        "issues":      [],
    }

    script = r"""
$os  = Get-CimInstance Win32_OperatingSystem
$mem = Get-CimInstance Win32_PhysicalMemory

$totalBytes = $os.TotalVisibleMemorySize * 1KB
$freeBytes  = $os.FreePhysicalMemory    * 1KB
$usedBytes  = $totalBytes - $freeBytes
$usagePct   = [math]::Round(($usedBytes / $totalBytes) * 100, 1)
$speedMHz   = ($mem | Measure-Object Speed -Maximum).Maximum
$slotsUsed  = ($mem | Measure-Object).Count

# Memory type lookup
$typeMap = @{0="Unknown";1="Other";2="DRAM";3="SDRAM";4="RDRAM";5="EDO";
             17="SDRAM";18="DDR";19="DDR2";20="DDR2 FB-DIMM";24="DDR3";
             26="DDR4";34="DDR5"}
$memTypeVal = ($mem | Select-Object -First 1).SMBIOSMemoryType
$memType = if ($typeMap.ContainsKey([int]$memTypeVal)) { $typeMap[[int]$memTypeVal] } else { "DDR" }

@{
    TotalBytes = $totalBytes
    FreeBytes  = $freeBytes
    UsedBytes  = $usedBytes
    UsagePct   = $usagePct
    SpeedMHz   = $speedMHz
    SlotsUsed  = $slotsUsed
    MemType    = $memType
} | ConvertTo-Json -Compress
"""
    rc, stdout, _ = run_powershell(script)
    if rc == 0 and stdout:
        import json
        try:
            data = json.loads(stdout)
            total = float(data.get("TotalBytes", 0))
            free  = float(data.get("FreeBytes", 0))
            used  = float(data.get("UsedBytes", 0))
            result["total_gb"]   = round(total / (1024**3), 1)
            result["free_gb"]    = round(free  / (1024**3), 1)
            result["used_gb"]    = round(used  / (1024**3), 1)
            result["usage_pct"]  = float(data.get("UsagePct", 0))
            result["speed_mhz"]  = int(data.get("SpeedMHz", 0) or 0)
            result["slots_used"] = int(data.get("SlotsUsed", 0) or 0)
            result["type"]       = str(data.get("MemType", "Unknown"))
        except Exception:
            pass

    score  = 100
    issues = []

    usage = result["usage_pct"]
    total = result["total_gb"]

    if usage >= 90:
        score -= 40
        issues.append(f"RAM critically full ({usage:.0f}%)")
    elif usage >= 75:
        score -= 20
        issues.append(f"RAM heavily used ({usage:.0f}%)")
    elif usage >= 60:
        score -= 10
        issues.append(f"RAM usage elevated ({usage:.0f}%)")

    if total < 4:
        score -= 25
        issues.append(f"Very low RAM ({total:.1f} GB)")
    elif total < 8:
        score -= 10
        issues.append(f"Low RAM ({total:.1f} GB)")

    result["score"]  = clamp(score, 0, 100)
    result["issues"] = issues
    return result
