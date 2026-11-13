"""Run CCI's unchanged generator against an existing modular Boost checkout."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STACKTRACE_DUMP_USERS = (
    "stacktrace_addr2line", "stacktrace_backtrace", "stacktrace_basic",
    "stacktrace_from_exception", "stacktrace_windbg", "stacktrace_windbg_cached",
)


def require_clean(directory):
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all", "--ignore-submodules=all"],
        cwd=directory, text=True)
    if dirty:
        raise ValueError(f"Modified source checkout: {directory}\n{dirty}")


def validate_checkout(directory):
    require_clean(directory)
    tree = subprocess.check_output(["git", "ls-tree", "-r", "HEAD"], cwd=directory, text=True)
    for line in tree.splitlines():
        metadata, relative = line.split("\t", 1)
        mode, kind, commit = metadata.split()
        if mode != "160000":
            continue
        child = directory / relative
        actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=child, text=True).strip()
        if actual != commit:
            raise ValueError(f"Submodule {child} does not match its pinned commit")
        validate_checkout(child)


def complete_metadata(data):
    # CCI's scanner misses these Jamfile requirements in Boost 1.92.
    # Keep corrections here so regeneration produces the reviewed metadata.
    if str(data["version"]) == "1.92.0":
        for backend in STACKTRACE_DUMP_USERS:
            data["dependencies"][backend] = sorted(set(data["dependencies"][backend]) | {"stacktrace_dump"})
        data["requirements"]["locale"] = sorted(set(data["requirements"]["locale"]) | {"iconv"})
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--boostdep", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    tag = f"boost-{args.version}"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    tagged = subprocess.check_output(["git", "rev-parse", f"{tag}^{{commit}}"], cwd=source, text=True).strip()
    if head != tagged:
        parser.error("Source HEAD must match the requested official Boost tag")
    try:
        validate_checkout(source)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    path = ROOT / "recipes/boost/all/rebuild-dependencies.py"
    spec = importlib.util.spec_from_file_location("cci_boost_dependencies", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    class Builder(module.BoostDependencyBuilder):
        @property
        def boost_path(self):
            return source

    builder = Builder(args.version, args.version, source.parent, "",
                      ROOT / "recipes/boost/all/dependencies", False)
    builder._boostdep = args.boostdep.resolve()
    builder.do_create_dependency_file()
    import yaml
    output = ROOT / "recipes/boost/all/dependencies" / f"dependencies-{args.version}.yml"
    data = complete_metadata(yaml.safe_load(output.read_text()))
    output.write_text(yaml.safe_dump(data, sort_keys=True))


if __name__ == "__main__":
    main()
