export DESIGN_NICKNAME = rb_bus_d8_r4
export DESIGN_NAME     = mmio_top
export PLATFORM        = sky130hd
export VERILOG_FILES   = /home/aru/Register-Bus/rtl/regfile.v /home/aru/Register-Bus/rtl/mmio_top.v
export VERILOG_DEFINES = -D P_DEPTH=8 -D P_NREAD=4 -D P_BYPASS=0
export SDC_FILE        = /home/aru/Register-Bus/runs/bus_d8_r4/constraint.sdc
export CORE_UTILIZATION = 40
export PLACE_DENSITY_LB_ADDON = 0.20
export TNS_END_PERCENT = 100
