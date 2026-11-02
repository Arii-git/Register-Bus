"""Tests for the register file behind the memory-mapped bus (bus design)."""
import os, random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer

D = int(os.environ.get("DEPTH", 8))
R = int(os.environ.get("NREAD", 2))
B = int(os.environ.get("BYPASS", 0))
W = 16
AW = (D - 1).bit_length()
MASK = (1 << W) - 1

DATA_BASE = 0
CTRL_BASE = 1 << AW
CTRL, STATUS, INPUT = CTRL_BASE + 0, CTRL_BASE + 1, CTRL_BASE + 2
UNMAPPED_A = CTRL_BASE + 3
UNMAPPED_B = 2 << AW


class Bus:
    def __init__(self, dut):
        self.dut = dut

    async def reset(self):
        d = self.dut
        cocotb.start_soon(Clock(d.clk, 10, units="ns").start())
        d.rst.value = 1
        d.sel.value = 0
        d.we.value = 0
        d.addr.value = 0
        d.wdata.value = 0
        d.scan_addr.value = 0
        d.in_port.value = 0
        await RisingEdge(d.clk)
        await FallingEdge(d.clk)
        d.rst.value = 0

    async def write(self, a, v):
        d = self.dut
        await FallingEdge(d.clk)
        d.sel.value = 1
        d.we.value = 1
        d.addr.value = a
        d.wdata.value = v
        await Timer(1, units="ns")
        err = int(d.err.value)
        await RisingEdge(d.clk)
        await FallingEdge(d.clk)
        d.sel.value = 0
        d.we.value = 0
        return err

    async def read(self, a):
        d = self.dut
        await FallingEdge(d.clk)
        d.sel.value = 1
        d.we.value = 0
        d.addr.value = a
        await Timer(1, units="ns")
        v = int(d.rdata.value)
        err = int(d.err.value)
        await RisingEdge(d.clk)
        await FallingEdge(d.clk)
        d.sel.value = 0
        return v, err
@cocotb.test()
async def reset_state(dut):
    b = Bus(dut)
    await b.reset()
    for a in range(D):
        assert await b.read(DATA_BASE + a) == (0, 0)
    assert await b.read(CTRL) == (0, 0)
    assert await b.read(STATUS) == (0, 0)
    assert await b.read(INPUT) == (0, 0)
