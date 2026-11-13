"""Build the recipe and exercise the public CMake targets used by Knuth."""
import argparse
import json
import pathlib
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED = {"atomic", "chrono", "container", "date_time", "exception", "thread"}


def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="1.92.0")
    parser.add_argument("--mode", choices=("headers", "native-minimal"), required=True)
    parser.add_argument("--compiler")
    parser.add_argument("--compiler-version")
    args = parser.parse_args()
    profile = str(ROOT / "profiles" / args.mode)
    common = ("-pr:h", profile, "-pr:b", "default", "-s:b", "compiler.cppstd=23")
    if args.compiler or args.compiler_version:
        if not (args.compiler and args.compiler_version):
            parser.error("Provide both --compiler and --compiler-version")
        profiles = json.loads(subprocess.check_output(
            ["conan", "profile", "show", *common, "--format=json"], cwd=ROOT, text=True))
        for context in ("host", "build"):
            settings = profiles[context]["settings"]
            actual = (settings.get("compiler"), str(settings.get("compiler.version")))
            if actual != (args.compiler, args.compiler_version):
                raise RuntimeError(f"Wrong {context} compiler: {actual}")
    report = ROOT / "reports"
    report.mkdir(exist_ok=True)
    graph = report / f"{args.version}-{args.mode}.json"
    start = time.monotonic()
    run("conan", "create", "recipes/boost/all", "--version", args.version,
        *common, "--build=missing", "--format=json", "--out-file", str(graph))
    data = json.loads(graph.read_text())
    nodes = list(data["graph"]["nodes"].values())
    for node in nodes:
        cppstd = node.get("settings", {}).get("compiler.cppstd")
        if cppstd is not None and str(cppstd) != "23":
            raise RuntimeError(f"Non-C++23 graph node: {node.get('ref')} ({cppstd})")
    package = next(n for n in nodes if str(n.get("ref", "")).startswith(f"boost/{args.version}#"))
    folder = pathlib.Path(package["package_folder"])
    # Inspect actual artifacts, including Windows static libraries.
    libraries = set()
    for lib in (folder / "lib").glob("*"):
        name = lib.name
        for prefix in ("libboost_", "boost_"):
            if name.startswith(prefix) and lib.suffix in (".a", ".lib", ".so", ".dylib", ".dll"):
                libraries.add(name[len(prefix):].split(".")[0].split("-")[0])
    expected = set() if args.mode == "headers" else EXPECTED
    if libraries != expected:
        raise RuntimeError(f"Unexpected compiled libraries: {libraries}; expected {expected}")
    run("conan", "test", "consumer", package["ref"], *common)
    print(json.dumps({"version": args.version, "mode": args.mode,
                      "libraries": sorted(libraries),
                      "seconds": round(time.monotonic() - start, 1)}, indent=2))


if __name__ == "__main__":
    main()
