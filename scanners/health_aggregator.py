"""
WinHub — System Health Aggregator
Runs all scanners and computes overall score + letter grade.
Author: ricinus (https://github.com/ricinuss)
"""
import threading
from core.constants import SCORE_GRADE
from core.utils import score_to_grade


WEIGHTS = {
    "cpu":      0.20,
    "ram":      0.20,
    "disk":     0.20,
    "startup":  0.15,
    "services": 0.15,
    "power":    0.10,
}


def run_all_scanners(progress_cb=None) -> dict:
    """
    Run all scanners. progress_cb(name, pct) called per step.
    Returns the full health report dict.
    """
    from scanners.cpu_scanner      import scan_cpu
    from scanners.ram_scanner      import scan_ram
    from scanners.disk_scanner     import scan_disk
    from scanners.startup_scanner  import scan_startup
    from scanners.services_scanner import scan_services
    from scanners.power_scanner    import scan_power, scan_temperature

    steps = [
        ("cpu",         scan_cpu),
        ("ram",         scan_ram),
        ("disk",        scan_disk),
        ("startup",     scan_startup),
        ("services",    scan_services),
        ("power",       scan_power),
        ("temperature", scan_temperature),
    ]

    report = {}
    total  = len(steps)

    for idx, (key, fn) in enumerate(steps):
        if progress_cb:
            progress_cb(key, int((idx / total) * 100))
        try:
            report[key] = fn()
        except Exception as e:
            report[key] = {"score": 50, "issues": [f"Scan error: {e}"]}

    if progress_cb:
        progress_cb("done", 100)

    # Weighted overall score (temperature is bonus — not penalized if unavailable)
    weighted = 0.0
    for key, weight in WEIGHTS.items():
        s = report.get(key, {}).get("score", 50)
        weighted += s * weight

    # Temperature: only subtract if available
    temp_data = report.get("temperature", {})
    if temp_data.get("available"):
        # Blend temp into score with a small weight, replacing 5% from power
        temp_score = temp_data.get("score", 100)
        weighted = weighted * 0.95 + temp_score * 0.05

    overall = round(weighted, 1)
    grade, grade_color = score_to_grade(overall)

    # Collect all issues
    all_issues = []
    for key in ("cpu", "ram", "disk", "startup", "services", "power", "temperature"):
        for iss in report.get(key, {}).get("issues", []):
            all_issues.append(iss)

    report["_summary"] = {
        "overall_score": overall,
        "grade":         grade,
        "grade_color":   grade_color,
        "issues":        all_issues,
    }

    return report
