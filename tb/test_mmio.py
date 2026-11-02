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

def scan_word(dut, p):
    v = int(dut.scan_data.value)
    return (v >> (p * W)) & MASK

@cocotb.test()
async def reset_state(dut):
    b = Bus(dut)
    await b.reset()
    for a in range(D):
        assert await b.read(DATA_BASE + a) == (0, 0)
    assert await b.read(CTRL) == (0, 0)
    assert await b.read(STATUS) == (0, 0)
    assert await b.read(INPUT) == (0, 0)
@cocotb.test()
async def data_region_write_read(dut):
    b = Bus(dut)
    await b.reset()
    vals = [random.getrandbits(W) for _ in range(D)]
    for a in range(D):
        assert await b.write(DATA_BASE + a, vals[a]) == 0
    for a in range(D):
        assert await b.read(DATA_BASE + a) == (vals[a], 0)

@cocotb.test()
async def ctrl_register_behaviour(dut):
    b = Bus(dut)
    await b.reset()
    await b.write(CTRL, 0x7ABC)
    assert (await b.read(CTRL))[0] == 0x7ABC
    await b.write(CTRL, 0xFFFF)
    assert (await b.read(CTRL))[0] == 0x7FFF

@cocotb.test()
async def unmapped_access_sets_error(dut):
    b = Bus(dut)
    await b.reset()
    for a in (UNMAPPED_A, UNMAPPED_B, (3 << AW) + 1):
        v, e = await b.read(a)
        assert (v, e) == (0, 1), f"addr {a}: {v:#x}, err {e}"
        assert await b.write(a, 0x1234) == 1
    st, _ = await b.read(STATUS)
    assert (st >> 8) & 1 == 1, "sticky error not set"

@cocotb.test()
async def write_counter_and_clear(dut):
    b = Bus(dut)
    await b.reset()
    for i in range(5):
        await b.write(DATA_BASE + (i % D), i)
    assert (await b.read(STATUS))[0] & 0xFF == 5
    await b.write(CTRL, 0x8000)
    assert (await b.read(STATUS))[0] == 0
    for i in range(260):
        await b.write(DATA_BASE, i & MASK)
    assert (await b.read(STATUS))[0] & 0xFF == 260 % 256
    await b.write(UNMAPPED_B, 1)
    assert (await b.read(STATUS))[0] >> 8 == 1
    await b.write(CTRL, 0x8000)
    assert (await b.read(STATUS))[0] == 0
@cocotb.test()
async def input_register(dut):
    b = Bus(dut)
    await b.reset()
    dut.in_port.value = 0xBEEF
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert (await b.read(INPUT))[0] == 0xBEEF
    dut.in_port.value = 0x1234
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert (await b.read(INPUT))[0] == 0x1234

@cocotb.test()
async def idle_bus_reads_zero(dut):
    b = Bus(dut)
    await b.reset()
    await b.write(DATA_BASE, 0xFFFF)
    await FallingEdge(dut.clk)
    dut.sel.value = 0
    dut.addr.value = DATA_BASE
    await Timer(1, units="ns")
    assert int(dut.rdata.value) == 0

@cocotb.test()
async def scan_ports(dut):
    if R < 2:
        return
    b = Bus(dut)
    await b.reset()
    vals = [random.getrandbits(W) for _ in range(D)]
    for a in range(D):
        await b.write(DATA_BASE + a, vals[a])
    dut.scan_addr.value = sum((p % D) << ((p - 1) * AW) for p in range(1, R))
    await Timer(1, units="ns")
    assert int(dut.scan_data.value) == 0, "scan data must be 0 while SCAN_EN = 0"
    await b.write(CTRL, 0x0001)
    dut.scan_addr.value = sum((p % D) << ((p - 1) * AW) for p in range(1, R))
    await Timer(1, units="ns")
    for p in range(1, R):
        assert scan_word(dut, p - 1) == vals[p % D]

@cocotb.test()
async def scan_port_bypass_behaviour(dut):
    if R < 2:
        return
    b = Bus(dut)
    await b.reset()
    await b.write(CTRL, 0x0001)
    await b.write(DATA_BASE + 1, 0x1111)
    await FallingEdge(dut.clk)
    dut.scan_addr.value = sum(1 << ((p - 1) * AW) for p in range(1, R))
    dut.sel.value = 1
    dut.we.value = 1
    dut.addr.value = DATA_BASE + 1
    dut.wdata.value = 0x2222
    await Timer(1, units="ns")
    expect = 0x2222 if B else 0x1111
    assert scan_word(dut, 0) == expect, f"BYPASS={B}: {scan_word(dut, 0):#x}"
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.sel.value = 0
    dut.we.value = 0

@cocotb.test()
async def random_bus_traffic(dut):
    b = Bus(dut)
    await b.reset()
    model = [0] * D
    ctrl = 0
    n = int(os.environ.get("TRAFFIC", 1500))
    for _ in range(n):
        a = random.randrange(D)
        if random.random() < 0.5:
            v = random.getrandbits(W)
            await b.write(DATA_BASE + a, v)
            model[a] = v
        else:
            assert await b.read(DATA_BASE + a) == (model[a], 0)
        if random.random() < 0.05:
            ctrl = random.getrandbits(W) & 0x7FFF
            await b.write(CTRL, ctrl)
            assert (await b.read(CTRL))[0] == ctrl
