"""
WinHub — Disk Scanner
Author: ricinus (https://github.com/ricinuss)
"""
from core.utils import run_powershell, clamp, format_bytes


def scan_disk() -> dict:
    result = {
        "drives":     [],
        "score":      50,
        "issues":     [],
    }

    script = r"""
$disks = Get-CimInstance Win32_DiskDrive | ForEach-Object {
    $disk = $_
    $partitions = Get-CimAssociatedInstance $disk -ResultClassName Win32_DiskPartition
    $logicals = $partitions | ForEach-Object {
        Get-CimAssociatedInstance $_ -ResultClassName Win32_LogicalDisk
    }
    foreach ($ld in $logicals) {
        [PSCustomObject]@{
            Letter     = $ld.DeviceID
            Model      = $disk.Model.Trim()
            MediaType  = $disk.MediaType
            SizeBytes  = $ld.Size
            FreeBytes  = $ld.FreeSpace
            UsagePct   = if ($ld.Size -gt 0) { [math]::Round((($ld.Size - $ld.FreeSpace) / $ld.Size) * 100, 1) } else { 0 }
            Serial     = $disk.SerialNumber.Trim()
        }
    }
}
$disks | ConvertTo-Json -Compress -Depth 3
"""
    rc, stdout, _ = run_powershell(script)
    drives = []
    if rc == 0 and stdout and stdout != "null":
        import json
        try:
            raw = json.loads(stdout)
            if isinstance(raw, dict):
                raw = [raw]
            for d in raw:
                size_b  = float(d.get("SizeBytes") or 0)
                free_b  = float(d.get("FreeBytes") or 0)
                used_b  = size_b - free_b
                media   = str(d.get("MediaType", "")).lower()
                is_ssd  = "ssd" in media or "solid" in media or d.get("MediaType") == 4
                drives.append({
                    "letter":    d.get("Letter", "?"),
                    "model":     d.get("Model", "Unknown"),
                    "type":      "SSD" if is_ssd else "HDD",
                    "size_gb":   round(size_b / (1024**3), 1),
                    "free_gb":   round(free_b / (1024**3), 1),
                    "used_gb":   round(used_b / (1024**3), 1),
                    "usage_pct": float(d.get("UsagePct", 0)),
                })
        except Exception:
            pass

    # Fallback: use wmic logicaldisk
    if not drives:
        fb_script = r"""
Get-PSDrive -PSProvider FileSystem | ForEach-Object {
    [PSCustomObject]@{
        Letter   = "$($_.Name):"
        Used     = $_.Used
        Free     = $_.Free
        Total    = $_.Used + $_.Free
    }
} | ConvertTo-Json -Compress -Depth 2
"""
        rc2, stdout2, _ = run_powershell(fb_script)
        if rc2 == 0 and stdout2:
            import json
            try:
                raw = json.loads(stdout2)
                if isinstance(raw, dict):
                    raw = [raw]
                for d in raw:
                    total = float(d.get("Total") or 0)
                    free  = float(d.get("Free") or 0)
                    used  = float(d.get("Used") or 0)
                    if total == 0:
                        continue
                    drives.append({
                        "letter":    d.get("Letter", "?"),
                        "model":     "Unknown",
                        "type":      "Disk",
                        "size_gb":   round(total / (1024**3), 1),
                        "free_gb":   round(free  / (1024**3), 1),
                        "used_gb":   round(used  / (1024**3), 1),
                        "usage_pct": round((used / total) * 100, 1) if total else 0,
                    })
            except Exception:
                pass

    result["drives"] = drives
    score  = 100
    issues = []

    for d in drives:
        pct = d["usage_pct"]
        ltr = d["letter"]
        if pct >= 95:
            score -= 30
            issues.append(f"Drive {ltr} critically full ({pct:.0f}%)")
        elif pct >= 85:
            score -= 15
            issues.append(f"Drive {ltr} nearly full ({pct:.0f}%)")
        elif pct >= 70:
            score -= 5
            issues.append(f"Drive {ltr} getting full ({pct:.0f}%)")

    result["score"]  = clamp(score, 0, 100)
    result["issues"] = issues
    return result
