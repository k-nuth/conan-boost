"""Compare a CCI revision with the pristine import, without changing this checkout."""
import argparse
import json
from pathlib import Path
import subprocess
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def diff(left, right):
    # Compare source trees, excluding local Conan/CMake build products.
    with tempfile.TemporaryDirectory(prefix="boost-diff-") as tmp:
        base = Path(tmp)
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "build", "CMakeUserPresets.json")
        shutil.copytree(left, base / "baseline", ignore=ignore)
        shutil.copytree(right, base / "candidate", ignore=ignore)
        result = subprocess.run(["git", "diff", "--no-index", "--", "baseline", "candidate"], cwd=tmp)
        if result.returncode not in (0, 1):
            raise RuntimeError("git diff failed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="master", help="CCI revision to inspect")
    args = parser.parse_args()
    source = json.loads((ROOT / "upstream.json").read_text())
    with tempfile.TemporaryDirectory(prefix="boost-cci-") as tmp:
        path = Path(tmp)
        subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout",
                        source["repository"], tmp], check=True)
        subprocess.run(["git", "sparse-checkout", "set", source["path"]], cwd=tmp, check=True)
        subprocess.run(["git", "checkout", "--detach", args.ref], cwd=tmp, check=True)
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp, text=True).strip()
        print(f"CCI base: {source['commit']}\nCandidate: {revision}", flush=True)
        print("\nUPSTREAM CHANGES", flush=True)
        diff(ROOT / "upstream/boost", path / source["path"])
        print("\nLOCAL CHANGES TO KEEP OR RECONCILE", flush=True)
        diff(ROOT / "upstream/boost", ROOT / "recipes/boost")


if __name__ == "__main__":
    main()
