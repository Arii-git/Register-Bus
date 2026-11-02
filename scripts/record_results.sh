#!/bin/bash
# usage: ./scripts/record_results.sh [regfile|mmio_top]   (one design per run)
cd ~/Register-Bus
TOP=${1:?give regfile or mmio_top}
OUT=log/results_${TOP}.md
{
echo "# Results: $TOP"
echo
echo "Generated: $(date '+%Y-%m-%d %H:%M')"
echo "Simulator: Icarus Verilog 11.0, cocotb 1.9.2"
echo
echo "| Depth | Read ports | Bypass | Result |"
echo "| --- | --- | --- | --- |"
} > $OUT
for d in 8 16 32 64; do for r in 1 2 4; do for b in 0 1; do
  rf make -s -C tb TOP=$TOP DEPTH=$d NREAD=$r BYPASS=$b > /tmp/t.log 2>&1
  line=$(grep -o "TESTS=[0-9]* PASS=[0-9]* FAIL=[0-9]*" /tmp/t.log | tail -1)
  echo "| $d | $r | $b | ${line:-no result} |" >> $OUT
  sleep 2
done; done; done
echo "Wrote $OUT"
