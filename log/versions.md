# Toolchain versions (recorded 2026-10-31)

Tools run inside Docker (image rf-tools, built FROM the pinned ORFS image below).

- ORFS image: openroad/orfs@sha256:ca289d6df8401711a4ed310a83b5bd14fd42534d64b9b790bf5cbb02cc496278
- ORFS commit (host flow scripts): ef324e55542359491ab14565748df975766d90f5
- Yosys: 0.68+post
- OpenROAD: no version string (binary built without git info); identified by the image digest above
- iverilog and cocotb 1.9.2: installed in rf-tools
- Host: Windows 11, WSL2 Ubuntu 22.04, WSL memory 10 GB, swap 8 GB
