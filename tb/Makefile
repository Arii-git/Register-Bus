# usage:  make DEPTH=16 NREAD=2 BYPASS=0 TOP=mmio_top
SIM            ?= icarus
TOPLEVEL_LANG   = verilog
DEPTH          ?= 8
NREAD          ?= 2
BYPASS         ?= 0
TOP            ?= mmio_top
VERILOG_SOURCES = $(CURDIR)/../rtl/regfile.v $(CURDIR)/../rtl/mmio_top.v
TOPLEVEL        = $(TOP)
MODULE          = $(if $(filter mmio_top,$(TOP)),test_mmio,test_regfile)
COMPILE_ARGS   += -DP_DEPTH=$(DEPTH) -DP_NREAD=$(NREAD) -DP_BYPASS=$(BYPASS)
SIM_BUILD       = sim_build_$(TOP)_d$(DEPTH)_r$(NREAD)_b$(BYPASS)
export DEPTH NREAD BYPASS
include $(shell cocotb-config --makefiles)/Makefile.sim
