"""Read-only prerequisite report; does not install or build dependencies."""
import json
import platform
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
disk = shutil.disk_usage(root)
print(json.dumps({
    "system": platform.system(),
    "architecture": platform.machine(),
    "free_disk_bytes": disk.free,
    "tools": {name: shutil.which(name) for name in ("git", "cmake", "conan", "vcpkg")},
    "dependency_source_builds": "forbidden",
    "benchmark_status": "not_run",
}, indent=2))
