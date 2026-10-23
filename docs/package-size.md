# Measured local deployment archive

2026-10-23 UTC, Qt Core 6.11.1, macOS ARM64, Release. Run `python3 scripts/package_macos.py` after the successful Conan build. This script creates a local CLI ZIP, without uploading a release.

| Measurement | Bytes | MiB |
| --- | ---: | ---: |
| ZIP, deflate level 9 | 3,193,822 | 3.05 |
| Extracted regular-file sizes | 8,773,927 | 8.37 |
| Allocated filesystem size (`du -sk`) | 9,048,064 | 8.63 |

Filesystem allocation varies by filesystem. No extra stripping was performed. Ad-hoc signing can affect exact bytes on later runs.

The package contains the 71,472-byte executable, QtCore (7,176,128 bytes), PCRE2-16 (376,000 bytes), zlib (124,656 bytes), double-conversion (110,112 bytes), and 915,559 bytes of package-provided license/notice files. All four libraries' package-provided license directories were copied, including Qt's broader notices; this is not a license compliance audit.

The script resolves recursive non-system dependencies, copies only those libraries, replaces load paths with `@loader_path` paths, removes development rpaths, and ad-hoc signs and verifies the copied Mach-O files. Apple system libraries/frameworks are not bundled. No QtGui, QtWidgets, libffi, development headers or Conan tools/cache are included.

The actual ZIP was extracted with `ditto` into a separate temporary directory and executed with inherited DYLD/Conan variables removed. It printed `Qt Core 6.11.1`, and dyld tracing confirmed all four non-system runtime libraries loaded from the extracted release directory, without loading from `.deps`.

Artifacts remain local under `results/package-20261023T072718Z/`: the ZIP, extracted staging directory, `size-report.json`, and `relocated-run.log`. The original Conan cache and development executable were unchanged. The archive is locally ad-hoc signed, not Developer ID signed or notarized, and has not been tested on a second Mac or older macOS release. These are measured bytes for this CLI smoke example, not a Qt GUI application or a completed public release.
