#!/bin/bash
cd ~/Register-Bus
OUT=log/mutations_bus.md
{
echo "# Mutation tests: mmio_top.v"
echo
echo "Generated: $(date '+%Y-%m-%d %H:%M')"
echo
echo "| # | Break | Depth | Read ports | Bypass | Result | Caught |"
echo "| --- | --- | --- | --- | --- | --- | --- |"
} > $OUT
mutate() {
  n=$1; name=$2; expr=$3; d=$4; r=$5; b=$6
  git checkout -q rtl/mmio_top.v
  sed -i "$expr" rtl/mmio_top.v
  if git diff --quiet rtl/mmio_top.v; then
    echo "| $n | $name | $d | $r | $b | sed changed nothing | CHECK |" >> $OUT
    return
  fi
  rm -rf tb/sim_build_*
  rf make -s -C tb TOP=mmio_top DEPTH=$d NREAD=$r BYPASS=$b > /tmp/m.log 2>&1
  line=$(grep -o "TESTS=[0-9]* PASS=[0-9]* FAIL=[0-9]*" /tmp/m.log | tail -1)
  if echo "$line" | grep -q "FAIL=0"; then caught="NO"; elif [ -z "$line" ]; then caught="CHECK"; else caught="yes"; fi
  echo "| $n | $name | $d | $r | $b | ${line:-no result} | $caught |" >> $OUT
  git checkout -q rtl/mmio_top.v
}
mutate 1 "write counter adds 2" "s/wr_cnt + 8'd1/wr_cnt + 8'd2/" 8 2 0
mutate 2 "offset 3 treated as mapped" "s/is_ctrl \&\& (off != 2'b11)/is_ctrl/" 8 2 0
mutate 3 "scan gate removed" "s/ctrl_q\[0\] ? rf_rdata/1'b1 ? rf_rdata/" 8 2 0
mutate 4 "bypass ignored" "s/\.BYPASS(BYPASS)/.BYPASS(0)/" 8 2 1
git checkout -q rtl/mmio_top.v
echo "Wrote $OUT"
