# First vcpkg binary-only check

Run: 2026-10-23 UTC, macOS ARM64, Xcode Apple Clang 17, `arm64-osx` host and target. Tool version: `2026-09-26-51bf87ca6e9bf3e622d84ff323bd202ab1ca0c0b`; repository baseline: `40a678a192636131f04b3af79ba118d869effade`.

## Setup

The official tool was downloaded by `bootstrap-vcpkg.sh -disableMetrics`. A filtered clone and sparse checkout reduced repository storage. Tool setup was outside the timed installation attempt.

```sh
git clone --filter=blob:none --no-checkout https://github.com/microsoft/vcpkg.git .deps/tools/vcpkg
git -C .deps/tools/vcpkg sparse-checkout set --no-cone '/bootstrap-vcpkg.sh' '/scripts/' '/.vcpkg-root' '/triplets/' '/versions/'
git -C .deps/tools/vcpkg checkout 40a678a192636131f04b3af79ba118d869effade
(cd .deps/tools/vcpkg && ./bootstrap-vcpkg.sh -disableMetrics)
python3 scripts/try_vcpkg.py
```

The script sets explicit local download, registry, installation, build and package directories and `VCPKG_BINARY_SOURCES=clear;files,<project>/.deps/binary-cache,read`. That binary cache was empty. There was no remote binary cache configured.

## Result

- Exit code: 1, after 30.980 seconds.
- Restored binaries: 0. Installation stopped while handling the first uncached package, `vcpkg-cmake-config`.
- Qt and dependency source builds: none. No Qt library installed.
- Compiler detection ran and generated probe build files. `--only-binarycaching` prevents dependency source builds; it does not prevent compiler detection or tool downloads.
- vcpkg downloaded and extracted Ninja 1.13.2. Download directory occupied about 1.1 MiB afterwards; build-tree metadata and compiler detection occupied about 1.7 MiB.
- Total project `.deps` allocated size before/after the timed attempt: 126,480 / 191,892 KiB. This includes Conan tools and state from prior checks, plus the vcpkg repository. It is not Qt installation size. Repository metadata and lazy Git object retrieval contribute to the increase.
- vcpkg tool repository occupied about 95 MiB afterwards. Peak disk use was not measured.
- Raw log and report remain local under `results/20261023T061346Z-vcpkg.*`.

The plan contained Qt Base 6.8.3 with `core,cups,doubleconversion,thread`, plus double-conversion, libb2, pcre2, zlib and vcpkg helper ports. This differs from the Conan configuration. `default-features=false` does not remove every platform-selected requirement.

## Interpretation

The binary-only guard worked with an empty cache. The plan heading said packages would be “built and installed”, but that heading was not evidence of actual source compilation: installation failed on the uncached helper package without building dependencies.

This is an expected failure with no binary provider, not a failed public binary download and not a speed comparison. A successful restore requires a compatible populated binary cache. The earlier Conan failure had a different cause: its public remote lacked a Qt binary for the selected minimal configuration. Comparing 30.980 seconds against 3.583 seconds would not establish which tool installs Qt faster.
