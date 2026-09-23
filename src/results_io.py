"""Save and load run results as JSON files (read later by experiments/plot_results.py)."""

import json
import platform
from datetime import datetime
from pathlib import Path

RESULTS_DIR = Path("results")


def machine_info():
    """Describe the computer, to show that all runs used the same conditions."""
    return {
        "date": datetime.now().isoformat(timespec="seconds"),
        "os": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "python": f"{platform.python_implementation()} {platform.python_version()}",
    }


def save_json(name, parameters, results, out_dir=RESULTS_DIR):
    """Write results/<name>.json with machine info, parameters and results."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "experiment": name,
        "machine": machine_info(),
        "parameters": parameters,
        "results": results,
    }
    path = out_dir / f"{name}.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
