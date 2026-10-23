# Successful binary-only Conan installation

2026-10-23 UTC, macOS ARM64, Apple Clang 17, Release, GNU C++17, Conan 2.33.0. Qt 6.11.1 shared libraries were installed from ConanCenter and the Core-only application built and ran successfully.

## What resolved the mismatch

The earlier command set only `qt/*:shared=True`. Qt's dependency libraries still used their default static configurations. The published shared Qt package instead matched shared dependencies. Setting `*:shared=True` selected Qt package ID `df463a0ddc301b57fb64da60447cf7d388983235`, recipe revision `b4b7bf63674c82b58b825ffca311f656`, package revision `af543e3905979fcd4a7085dc4d9a3501`.

One transitive dependency, libffi 3.4.8, had macOS ARM64 packages built with Apple Clang 13, but not 17 under its current recipe. The committed host profile explicitly selects that published C shared-library binary using `libffi/*:compiler.version=13`. All other host packages and the application retain Apple Clang 17. No compiler binaries or package metadata were modified, and binary compatibility checks were not disabled. This is a narrow binary selection for this experiment, not a general guarantee that different compiler configurations are interchangeable.

No dependency version overrides or relaxed package-ID policies were necessary. The Qt package and its fuller defaults were accepted. The minimal original options remain archived under `profiles/`.

## Measured results

| Item | Result |
| --- | --- |
| Binary-only Conan install | Success, exit 0 |
| Dependency binary packages downloaded | 24 |
| Install wall time | 4.586 seconds |
| Dependency source builds | 0 (`--build=never`) |
| Qt package extracted allocated size | About 68 MiB |
| Entire isolated Conan home | About 181 MiB |
| Python environment plus Conan tool | About 28 MiB |
| CMake application build folder | About 2.2 MiB |
| Peak disk use | Not measured |

The installation timer excludes Python/Conan setup and earlier recipe/metadata queries. Binary packages were absent before this successful run, while recipe metadata was already cached. These are single-run observations, not a general speed benchmark or a comparison against vcpkg. The Conan home includes extracted dependencies and metadata from prior checks; it is not a compressed download total. vcpkg's existing tool directory is separate and excluded from the Conan-home figure.

`conan.lock` pins resolved recipe versions/revisions. It does not pin binary package revisions; the Qt binary revision used above is recorded explicitly for audit. Raw installation report/log: local `results/20261023T072130Z-conan.*`.

## Validation and runtime scope

The application was compiled with Apple Clang 17, linked to `Qt6::Core`, and printed `Qt Core 6.11.1`. CTest passed 1/1. `otool -L` on the executable showed QtCore and system libraries, without QtGui or QtWidgets. QtCore itself references the non-system libraries zlib, double-conversion and PCRE2, plus Apple system libraries/frameworks.

GUI plugins, SQL drivers, GLib and the older libffi binary were installed but not exercised by this Core-only smoke test. This validates the requested application, not every component of the fuller SDK. The executable currently uses build-time paths/rpaths into the local cache; it has not been packaged for distribution. Removing `.deps/conan` will break this development executable until dependencies are restored.

## Reproduce

Use the commands in the root README and the committed `profiles/macos-arm64` profile. Always retain `--build=never`. Conan uses the project-local `CONAN_HOME`, and tool installation lives under `.deps/tools/conan`; neither requires a global Qt installation.

For compatibility rules see [Conan dependency package IDs](https://docs.conan.io/2/reference/binary_model/dependencies.html).
