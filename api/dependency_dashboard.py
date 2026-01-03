import json
import subprocess
from fastapi import APIRouter

router = APIRouter()

def get_installed_packages():
    result = subprocess.run(
        ["pip", "freeze"],
        capture_output=True,
        text=True
    )
    return result.stdout.splitlines()

def get_required_packages():
    with open("requirements.txt") as f:
        return [line.strip() for line in f.readlines()]

@router.get("/admin/dependencies")
def dependency_status():
    installed = set(get_installed_packages())
    required = set(get_required_packages())

    missing = sorted(list(required - installed))
    extra = sorted(list(installed - required))

    return {
        "status": "ok" if not missing and not extra else "drift_detected",
        "missing_packages": missing,
        "extra_packages": extra,
        "installed_count": len(installed),
        "required_count": len(required),
    }
