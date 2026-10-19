# ERPNext-specific checks, called by check.py at the end.
# erpnext_checks.py is the checker a model wrote for this system: fields exist in DocType JSON,
# conversions exist in mappers, status options, translations, settings defaults.
import subprocess, sys
from pathlib import Path


def check(ont, error, warn):
    here = Path(__file__).resolve().parent
    r = subprocess.run([sys.executable, str(here / "erpnext_checks.py")], capture_output=True, text=True, cwd=ont.root)
    for line in (r.stdout + r.stderr).splitlines():
        if line.startswith("FAIL"):
            error("erpnext: " + line[4:].strip())
        elif line.startswith("note"):
            warn("erpnext: " + line.split(":", 1)[1].strip())
    if r.returncode not in (0, 1):
        error(f"erpnext_checks.py crashed: {r.stderr.strip()[-300:]}")
