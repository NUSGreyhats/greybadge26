module led_mmio (
    input wire clk,
    input wire rst,
    input wire valid,
    input wire wen,
    input wire [7:0] addr,
    input wire [31:0] wdata,
    output reg [31:0] rdata,
    output wire [7:0] leds
);
    reg [7:0] led_reg;

    assign leds = led_reg;

    always @(posedge clk) begin
        if (rst) begin
            led_reg <= 8'h00;
        end else if (valid && wen && addr == 8'h00) begin
            led_reg <= wdata[7:0];
        end
    end

    always @(*) begin
        rdata = (addr == 8'h00) ? {24'h0, led_reg} : 32'h0000_0000;
    end
endmodule
