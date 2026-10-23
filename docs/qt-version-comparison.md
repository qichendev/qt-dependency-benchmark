# Qt version binary metadata comparison

**Follow-up:** [Qt 6.11.1 installation succeeded](conan-success.md) after selecting shared dependencies and the published libffi binary. The default-options failures below describe the earlier Qt-only shared setting, not all supported configurations.

Queried ConanCenter on 2026-10-23 UTC using `conan list qt/*` followed by `conan list qt/VERSION:*` for all 19 listed Qt 6 versions. Counts refer to package IDs under the latest recipe revision, not package revisions or every historical recipe. No archive bodies were downloaded.

| Qt version | All-platform package IDs | macOS ARM64 package IDs | Apple Clang versions |
| --- | ---: | ---: | --- |
| 6.3.2 | 5 | 1 | 13 |
| 6.4.1 | 3 | 0 | — |
| 6.4.2 | 5 | 1 | 13 |
| 6.5.0 / 6.5.1 / 6.5.2 | 5 each | 0 | — |
| 6.5.3 | 0 | 0 | — |
| 6.6.0 | 5 | 1 | 13 |
| 6.6.1 / 6.6.2 | 4 each | 0 | — |
| 6.6.3 | 0 | 0 | — |
| 6.7.0 / 6.7.1 | 4 each | 0 | — |
| 6.7.3 | 0 | 0 | — |
| 6.8.3 | 10 | 2 | 17 |
| 6.10.1 | 8 | 2 | 17 |
| 6.10.3 | 10 | 2 | 17 |
| 6.11.0 | 8 | 2 | 17 |
| 6.11.1 | 30 | 6 | 17 |

None of the queried macOS ARM64 packages had both `gui=False` and `widgets=False`. The six 6.11.1 packages comprise three static and three shared Release packages, all enabling GUI and Widgets. More IDs do not necessarily mean more module configurations: dependency identities also affect package IDs.

An additional metadata-only graph check for Qt 6.11.1 with default options, `shared=True`, macOS ARM64, Apple Clang 17, Release, `compiler.cppstd=gnu17` and `--build=never` still reported Qt binary ID `d7e983790cd858b6f33e9a0f6d7cfdbf84b51a4c` missing. Although `graph info` exited zero, its graph explicitly contained missing packages; that exit code is not evidence of installability.

Conclusion: 6.11.1 has more published binary IDs, but simply changing the Qt version does not solve either the minimal-options mismatch or the currently resolved dependency graph mismatch. Matching published dependencies and options is the next step; historical recipe revisions have not been surveyed.

Reproduce the count survey with `scripts/compare_qt_versions.py` after generating `results/qt-versions.json` via the list command. Raw results are local under `results/qt-version-comparison.json` and per-version JSON files. The committed Qt dependency version remains unchanged.
