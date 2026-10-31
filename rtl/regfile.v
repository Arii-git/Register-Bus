// Parameterised flop-based register file.
// One write port (synchronous), NREAD read ports (combinational).
// Defaults come from macros so the flow can set them with -D P_DEPTH=16 etc.
`ifndef P_DEPTH
 `define P_DEPTH 8
`endif
`ifndef P_WIDTH
 `define P_WIDTH 16
`endif
`ifndef P_NREAD
 `define P_NREAD 2
`endif
`ifndef P_BYPASS
 `define P_BYPASS 0
`endif

module regfile #(
  parameter DEPTH  = `P_DEPTH,
  parameter WIDTH  = `P_WIDTH,
  parameter NREAD  = `P_NREAD,
  parameter BYPASS = `P_BYPASS,
  parameter AW     = $clog2(DEPTH)
)(
  input  wire                   clk,
  input  wire                   rst,
  input  wire                   we,
  input  wire [AW-1:0]          waddr,
  input  wire [WIDTH-1:0]       wdata,
  input  wire [NREAD*AW-1:0]    raddr,
  output wire [NREAD*WIDTH-1:0] rdata
);
  reg [WIDTH-1:0] mem [0:DEPTH-1];
  integer i;

  always @(posedge clk) begin
    if (rst) begin
      for (i = 0; i < DEPTH; i = i + 1) mem[i] <= {WIDTH{1'b0}};
    end else if (we) begin
      mem[waddr] <= wdata;
    end
  end

  genvar p;
  generate
    for (p = 0; p < NREAD; p = p + 1) begin : rd
      wire [AW-1:0] a   = raddr[p*AW +: AW];
      wire          hit = (BYPASS != 0) && we && (waddr == a);
      assign rdata[p*WIDTH +: WIDTH] = hit ? wdata : mem[a];
    end
  endgenerate
endmodule
