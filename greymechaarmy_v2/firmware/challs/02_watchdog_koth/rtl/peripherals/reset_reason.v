`include "memory_map.vh"

module reset_reason (
    input wire clk,
    input wire rst,
    input wire valid,
    input wire wen,
    input wire [7:0] addr,
    input wire [31:0] wdata,
    input wire set_reason,
    input wire [31:0] reason_in,
    input wire [63:0] cycle_count,
    output reg [31:0] rdata,
    output reg [31:0] reason
);
    always @(posedge clk) begin
        if (rst) begin
            reason <= `RESET_CLEAN_BOOT;
        end else if (set_reason) begin
            reason <= reason_in;
        end else if (valid && wen && addr == 8'h00) begin
            reason <= wdata;
        end
    end

    always @(*) begin
        case (addr)
            8'h00: rdata = reason;
            8'h04: rdata = cycle_count[31:0];
            8'h08: rdata = cycle_count[63:32];
            default: rdata = 32'h0000_0000;
        endcase
    end
endmodule
