# Local environment recovery

The checkout moved from `D:/sih-2026/...` to `D:/me/CODING/Github/...`.
Existing CMake caches are historical artifacts; do not reuse/overwrite them.
The machine's global MinGW is 32-bit GCC6.3 and cannot run the frozen x64 core.

Installed a project-local portable WinLibs GCC14.2.0 x64 UCRT POSIX SEH r2,
matching the compiler version strings in frozen24. Source download:
https://github.com/brechtsanders/winlibs_mingw/releases/tag/14.2.0posix-19.1.1-12.0.0-ucrt-r2

Archive `winlibs-x86_64-posix-seh-gcc-14.2.0-mingw-w64ucrt-12.0.0-r2.7z`
SHA256 `e8751bcad522ee112fbc197e6224c67811df6d039cf400269135eff0dad8cf0c`.
Verified against the release checksum before extracting. No global PATH or
machine installation change: prepend `tools/local-toolchain/mingw64/bin` in
the experiment process. Frozen24's `--version` now succeeds.

Python: bundled Codex Python3.12.14. Existing project reference dependencies
import successfully: HiGHS1.12.0 and NumPy2.5.3. Use `-B` and set
`PYTHONDONTWRITEBYTECODE=1` to preserve tracked historical dependency caches.
References remain Python-only and never feed points/bounds into our C++ core.

Build: fresh `build-milp-iter25`, Release, CMake MinGW Makefiles, four compiler
jobs. Timed solves remain serial and start after builds/checks. Historical
clock timings are not direct performance comparisons on this new environment.
