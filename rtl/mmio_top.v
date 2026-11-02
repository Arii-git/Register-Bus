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

module mmio_top #(
  parameter DEPTH  = `P_DEPTH,
  parameter WIDTH  = `P_WIDTH,
  parameter NREAD  = `P_NREAD,
  parameter BYPASS = `P_BYPASS,
  parameter AW     = $clog2(DEPTH),
  parameter SCW    = (NREAD > 1) ? (NREAD - 1) : 1
)(
  input  wire                 clk,
  input  wire                 rst,
  input  wire                 sel,
  input  wire                 we,
  input  wire [AW+1:0]        addr,
  input  wire [WIDTH-1:0]     wdata,
  output wire [WIDTH-1:0]     rdata,
  output wire                 err,
  input  wire [SCW*AW-1:0]    scan_addr,
  output wire [SCW*WIDTH-1:0] scan_data,
  input  wire [WIDTH-1:0]     in_port
);
  localparam ABITS = AW + 2;

  wire [1:0] region  = addr[ABITS-1:ABITS-2];
  wire [1:0] off     = addr[1:0];
  wire is_data   = (region == 2'b00);
  wire is_ctrl   = (region == 2'b01);
  wire ctrl_ok   = is_ctrl && (off != 2'b11);
  wire mapped    = is_data | ctrl_ok;
  assign err     = sel & ~mapped;


  wire wr_data   = sel & we & is_data;
  wire wr_ctrl   = sel & we & is_ctrl & (off == 2'b00);
  wire [NREAD*AW-1:0]    rf_raddr;
  wire [NREAD*WIDTH-1:0] rf_rdata;
  assign rf_raddr[AW-1:0] = addr[AW-1:0];
  genvar p;
  generate
    for (p = 1; p < NREAD; p = p + 1) begin : g_scan_addr
      assign rf_raddr[p*AW +: AW] = scan_addr[(p-1)*AW +: AW];
    end
  endgenerate
  regfile #(.DEPTH(DEPTH), .WIDTH(WIDTH), .NREAD(NREAD), .BYPASS(BYPASS)) u_rf (
    .clk(clk), .rst(rst),
    .we(wr_data), .waddr(addr[AW-1:0]), .wdata(wdata),
    .raddr(rf_raddr), .rdata(rf_rdata)
  );

  // ---- control / status / input registers ----
  reg [WIDTH-1:0] ctrl_q;
  reg [7:0]       wr_cnt;
  reg             err_sticky;
  reg [WIDTH-1:0] in_q;
  wire clear = wr_ctrl & wdata[15];

  always @(posedge clk) begin
    if (rst) begin
      ctrl_q     <= {WIDTH{1'b0}};
      wr_cnt     <= 8'd0;
      err_sticky <= 1'b0;
      in_q       <= {WIDTH{1'b0}};
    end else begin
      in_q <= in_port;
      if (wr_ctrl) ctrl_q <= wdata & {1'b0, {(WIDTH-1){1'b1}}};
      if (clear) begin
        wr_cnt     <= 8'd0;
        err_sticky <= 1'b0;
      end else begin
        if (wr_data) wr_cnt <= wr_cnt + 8'd1;
        if (err)     err_sticky <= 1'b1;
      end
    end
  end

  wire [WIDTH-1:0] status = {{(WIDTH-9){1'b0}}, err_sticky, wr_cnt};

  // ---- read mux ----
  reg [WIDTH-1:0] rd_mux;
  always @* begin
    rd_mux = {WIDTH{1'b0}};
    if (is_data) begin
      rd_mux = rf_rdata[WIDTH-1:0];
    end else if (is_ctrl) begin
      case (off)
        2'b00:   rd_mux = ctrl_q;
        2'b01:   rd_mux = status;
        2'b10:   rd_mux = in_q;
        default: rd_mux = {WIDTH{1'b0}};
      endcase
    end
  end
  assign rdata = sel ? rd_mux : {WIDTH{1'b0}};

  // ---- scan data ----
  generate
    if (NREAD > 1) begin : g_scan
      assign scan_data = ctrl_q[0] ? rf_rdata[NREAD*WIDTH-1:WIDTH] : {SCW*WIDTH{1'b0}};
    end else begin : g_noscan
      assign scan_data = {SCW*WIDTH{1'b0}};
    end
  endgenerate
endmodule
