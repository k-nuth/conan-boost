# Boost Conan recipe

Knuth-maintained packaging of **Boost 1.92.0**, based on Conan Center Index (CCI).
Only the latest supported version is listed in `recipes/boost/config.yml`.
The package remains `boost/1.92.0`; CCI's options, defaults and CMake component
names are preserved. No Knuth-specific option is required by consumers.

## Build and verify

Install Python, PyYAML, Conan 2.34.0 and CMake 4.4.4, then:

```sh
conan profile detect
python scripts/check.py --mode headers
python scripts/check.py --mode native-minimal
```

Use a separate `CONAN_HOME` to keep these recipe revisions apart from your CCI
cache. Both commands run the upstream test package and the focused consumer.
Both host and build contexts explicitly use C++23; graph inspection rejects
other declared C++ standards. Conan profile detection may initially report its
default (such as gnu17), which these explicit settings override.
The latter tests Unordered flat and concurrent maps, Bloom, Multiprecision,
Bimap and atomic shared pointers through `Boost::headers` and `Boost::boost`.
The native profile additionally tests shared mutexes through `Boost::thread`.
Checks remain enabled in Release builds. The script inspects the actual package
and rejects unexpected compiled Boost libraries.

- `profiles/headers`: all Boost headers, no compiled Boost libraries.
- `profiles/native-minimal`: static Thread and its dependency closure: Atomic,
  Chrono, Container, DateTime and Exception. Compression and Locale backends
  are disabled. This profile still needs native compilation.

These profiles are opt-in. The recipe keeps CCI's default behavior; the default
full-library build and every possible option combination are **not** certified
by this CI. Both focused profiles run with the project toolchains:

| Runner | Selected compiler |
| --- | --- |
| Ubuntu 24.04 | GCC 16 |
| macOS 26 | Xcode 26.6 / Apple Clang 21 |
| Windows 2025 | VS 2026 / MSVC toolset 14.44 (Conan 194) |

CI checks both detected host/build compiler versions before packaging; it does
not accept a runner's older default. Windows uses Ninja with VS version 18.
The GCC installer and archive signing key are imported from UTXO-Z commit
`a1e0cce48e905cbaa5991f243979fdb2b55279d0` and retain their original license header.

Knuth still uses Boost.Thread. Do not switch its whole build to the header-only
profile until those uses have been reviewed and replaced. Do not update the
Knuth or UTXO-Z version pins automatically: UTXO-Z persists Boost containers,
so a version upgrade needs separate disk-layout and compatibility checks.

## Track CCI changes

`upstream/boost` is the pristine historical import, including its old versions.
It is reference material, not the published recipe. `upstream.json` records its
exact CCI commit. The working recipe is under `recipes/boost`.

```sh
python scripts/compare-upstream.py --ref master
# Or use an exact CCI commit for a reproducible review.
```

This read-only tool shows changes from the recorded baseline to the requested
CCI revision, followed by our local delta. Review both before applying changes;
keep the latest-only version policy, source checksum and regenerated dependency
metadata. Update the pristine snapshot and `upstream.json` together only after
reviewing and reconciling the working recipe. Run both package checks again.
This avoids silently overwriting our changes or importing CCI updates blindly.

## Add a new Boost release

1. Verify the official source archive checksum against the release's JSON
   metadata at `archives.boost.io`. Update `config.yml` and `conandata.yml`,
   replacing the previous version rather than accumulating old versions.
2. Check out the official `boostorg/boost` release tag and initialize its pinned
   submodules. The flattened release archive is insufficient for boostdep's
   module dependency discovery. Build the matching official `boostdep` tool.
3. Regenerate the dependency data through the wrapper around CCI’s unchanged generator:

   ```sh
   python scripts/rebuild-dependencies.py --version 1.92.0 \
     --source /path/to/modular/boost --boostdep /path/to/boostdep
   ```

The wrapper rejects dirty checkouts, including staged, unstaged and untracked
   submodule inputs. For 1.92 it restores the optional Locale/iconv requirement
   and the compiled Stacktrace backends' dependency on stacktrace_dump, which
   CCI's scanner misses. These corrections are reapplied on regeneration.

4. Review the Thread closure and update the profile if it changed. Remove the
   old version's dependency metadata and obsolete patches. Validate both modes
   and review the source/ABI implications before publishing.

For 1.92.0 the official source commit is
`afdfa32505af73e3d208144b3f623f0096cb62b6`; its archive SHA-256 is pinned in
`conandata.yml`. The dependency file was generated from that modular checkout
and its pinned submodules using Boost 1.92's boostdep. The tooling executable
was linked against Boost 1.91 Filesystem/Atomic; package headers and binaries
come entirely from the verified 1.92 source archive.

## Additional component regression

The non-Windows `tests/stacktrace-consumer` links only `Boost::stacktrace_basic`
with `BOOST_STACKTRACE_LINK`; it verifies that `stacktrace_dump` is propagated.
To exercise it, create a package using `profiles/native-minimal` plus
`-o 'boost/*:without_stacktrace=False' -o 'boost/*:with_stacktrace_backtrace=False'`,
then run `conan test tests/stacktrace-consumer boost/1.92.0` with the same profile
and options, and C++23 in the build context. The regular matrix keeps
Stacktrace disabled, matching Knuth's focused profile.

## Publish

After the package matrix passes, configure the intended Conan remote and use
`conan upload 'boost/1.92.0#<reviewed-recipe-revision>' -r <remote> --confirm`.
Upload only the explicitly reviewed revision. This repository does not upload
packages automatically and does not change Knuth or UTXO-Z dependencies.

Recipe code retains CCI's MIT license. Boost itself uses the Boost Software
License, included in the source archive and Conan packages.
