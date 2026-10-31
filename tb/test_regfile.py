"""Tests for the bare register file (core-only design)."""
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


async def setup(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst.value = 1
    dut.we.value = 0
    dut.waddr.value = 0
    dut.wdata.value = 0
    dut.raddr.value = 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.rst.value = 0


def pack(addrs):
    return sum(a << (p * AW) for p, a in enumerate(addrs))


async def write(dut, a, d):
    await FallingEdge(dut.clk)
    dut.we.value = 1
    dut.waddr.value = a
    dut.wdata.value = d
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.we.value = 0


async def read_all(dut, addrs):
    dut.raddr.value = pack(addrs)
    await Timer(1, units="ns")
    v = int(dut.rdata.value)
    return [(v >> (p * W)) & MASK for p in range(R)]


@cocotb.test()
async def reset_clears_everything(dut):
    await setup(dut)
    for a in range(D):
        assert (await read_all(dut, [a] * R)) == [0] * R


@cocotb.test()
async def write_then_read_every_address(dut):
    await setup(dut)
    vals = [random.getrandbits(W) for _ in range(D)]
    for a in range(D):
        await write(dut, a, vals[a])
    for a in range(D):
        assert (await read_all(dut, [a] * R)) == [vals[a]] * R


@cocotb.test()
async def same_cycle_read_of_written_address(dut):
    await setup(dut)
    await write(dut, 1 % D, 0x1111)
    await FallingEdge(dut.clk)
    dut.we.value = 1
    dut.waddr.value = 1 % D
    dut.wdata.value = 0x2222
    got = await read_all(dut, [1 % D] * R)
    expect = 0x2222 if B else 0x1111
    assert got == [expect] * R, f"BYPASS={B}: got {got}, expected {expect:#x}"
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.we.value = 0
    assert (await read_all(dut, [1 % D] * R)) == [0x2222] * R


@cocotb.test()
async def no_write_when_we_is_low(dut):
    await setup(dut)
    await write(dut, 0, 0xAAAA)
    await FallingEdge(dut.clk)
    dut.we.value = 0
    dut.waddr.value = 0
    dut.wdata.value = 0x5555
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert (await read_all(dut, [0] * R))[0] == 0xAAAA


@cocotb.test()
async def random_traffic(dut):
    await setup(dut)
    model = [0] * D
    n = int(os.environ.get("TRAFFIC", 3000))
    for _ in range(n):
        await FallingEdge(dut.clk)
        we = random.randint(0, 1)
        wa = random.randrange(D)
        wd = random.getrandbits(W)
        ras = [random.randrange(D) for _ in range(R)]
        dut.we.value = we
        dut.waddr.value = wa
        dut.wdata.value = wd
        got = await read_all(dut, ras)
        for p, a in enumerate(ras):
            exp = wd if (B and we and wa == a) else model[a]
            assert got[p] == exp, f"port {p} addr {a}: got {got[p]:#x} exp {exp:#x}"
        await RisingEdge(dut.clk)
        if we:
            model[wa] = wd
