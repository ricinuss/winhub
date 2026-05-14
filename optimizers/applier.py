"""
WinHub — Tweak Applier
Executes registry, service, and PowerShell script tweaks.
Adapted from WinUtil's Invoke-WinUtilTweaks + Set-WinUtilRegistry pattern.
Author: ricinus (https://github.com/ricinuss)
"""
from core.utils import set_registry_value, run_powershell, run_powershell_live
from optimizers.tweaks_db import get_tweak_by_id


class TweakResult:
    def __init__(self, tweak_id: str, name: str):
        self.tweak_id = tweak_id
        self.name     = name
        self.success  = True
        self.errors   = []

    def fail(self, msg: str):
        self.success = False
        self.errors.append(msg)

    def __repr__(self):
        status = "OK" if self.success else f"FAIL({', '.join(self.errors)})"
        return f"<TweakResult {self.tweak_id}: {status}>"


def apply_tweak(tweak_id: str, progress_cb=None, live_output: bool = False) -> TweakResult:
    """
    Apply a single tweak by ID.
    progress_cb(msg: str) is called for status updates.
    """
    tweak = get_tweak_by_id(tweak_id)
    if not tweak:
        r = TweakResult(tweak_id, tweak_id)
        r.fail("Tweak not found in database")
        return r

    result = TweakResult(tweak_id, tweak["name"])

    def log(msg):
        if progress_cb:
            progress_cb(msg)

    # ── Registry entries ────────────────────────────────────────────────────
    for reg in tweak.get("registry", []):
        path  = reg["path"].replace("\\\\", "\\")
        name  = reg["name"]
        value = reg["value"]
        rtype = reg.get("type", "DWord")
        log(f"  REG  {path}\\{name} = {value}")
        ok = set_registry_value(path, name, value, rtype)
        if not ok:
            result.fail(f"Registry set failed: {name}")

    # ── Service startup types ───────────────────────────────────────────────
    for svc in tweak.get("service", []):
        name    = svc["name"]
        startup = svc["startup_type"]
        log(f"  SVC  {name} → {startup}")
        ps = f'Set-Service -Name "{name}" -StartupType {startup} -ErrorAction SilentlyContinue'
        rc, _, err = run_powershell(ps)
        if rc != 0 and err:
            result.fail(f"Service set failed: {name} — {err}")

    # ── PowerShell script ───────────────────────────────────────────────────
    script = tweak.get("script", "").strip()
    if script:
        log(f"  PS   Running script for {tweak['name']}…")
        if live_output:
            rc = run_powershell_live(script)
        else:
            rc, out, err = run_powershell(script, timeout=120)
            if err and "warning" not in err.lower():
                result.fail(f"Script error: {err[:120]}")

    return result


def apply_tweaks_batch(
    tweak_ids: list,
    progress_cb=None,
    step_cb=None,
) -> list[TweakResult]:
    """
    Apply multiple tweaks. 
    progress_cb(tweak_name, pct)  — overall progress
    step_cb(msg)                  — per-step log messages
    """
    results = []
    total   = len(tweak_ids)

    for idx, tid in enumerate(tweak_ids):
        tweak = get_tweak_by_id(tid)
        name  = tweak["name"] if tweak else tid

        if progress_cb:
            pct = int((idx / total) * 100)
            progress_cb(name, pct)

        r = apply_tweak(tid, progress_cb=step_cb)
        results.append(r)

    if progress_cb:
        progress_cb("Done", 100)

    return results


def undo_tweak(tweak_id: str, progress_cb=None) -> TweakResult:
    """Undo a single tweak — restores original registry values and runs undo script."""
    tweak = get_tweak_by_id(tweak_id)
    if not tweak:
        r = TweakResult(tweak_id, tweak_id)
        r.fail("Tweak not found")
        return r

    result = TweakResult(tweak_id, tweak["name"])

    def log(msg):
        if progress_cb:
            progress_cb(msg)

    # Restore registry originals
    for reg in tweak.get("registry", []):
        path  = reg["path"].replace("\\\\", "\\")
        name  = reg["name"]
        orig  = reg.get("original")
        rtype = reg.get("type", "DWord")
        if orig is not None:
            log(f"  UNDO REG {path}\\{name} = {orig}")
            set_registry_value(path, name, orig, rtype)

    # Restore services
    for svc in tweak.get("service", []):
        name = svc["name"]
        orig = svc.get("original_type", "Manual")
        log(f"  UNDO SVC {name} → {orig}")
        ps = f'Set-Service -Name "{name}" -StartupType {orig} -ErrorAction SilentlyContinue'
        run_powershell(ps)

    # Run undo script
    undo_script = tweak.get("undo", "").strip()
    if undo_script:
        log(f"  UNDO PS  {tweak['name']}…")
        run_powershell(undo_script, timeout=60)

    return result
