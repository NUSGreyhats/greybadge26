module flag_rom (
    input wire clk,
    input wire rst,
    input wire valid,
    input wire wen,
    input wire [7:0] addr,
    input wire [31:0] wdata,
    output reg [31:0] rdata
);
    localparam REG_LEN     = 8'hf0;
    localparam REG_STATUS  = 8'hf4;
    localparam REG_PROFILE = 8'hf8;

    localparam FLAG_LEN = 32'd16;
    localparam STATUS_PRESENT = 32'h0000_0001;
    localparam PROFILE_PUBLIC_FLAG = 32'h0000_0000;

    wire unused_clk = clk;
    wire unused_rst = rst;
    wire unused_valid = valid;
    wire unused_wen = wen;
    wire [31:0] unused_wdata = wdata;

    always @(*) begin
        if (addr == REG_LEN) begin
            rdata = FLAG_LEN;
        end else if (addr == REG_STATUS) begin
            rdata = STATUS_PRESENT;
        end else if (addr == REG_PROFILE) begin
            rdata = PROFILE_PUBLIC_FLAG;
        end else begin
            case (addr[7:2])
                6'd0: rdata = 32'h7965_7267; // grey
                6'd1: rdata = 32'h676f_647b; // {dog
                6'd2: rdata = 32'h6369_6b5f; // _kic
                6'd3: rdata = 32'h7d64_656b; // ked}
                default: rdata = 32'h0000_0000;
            endcase
        end
    end
endmodule
