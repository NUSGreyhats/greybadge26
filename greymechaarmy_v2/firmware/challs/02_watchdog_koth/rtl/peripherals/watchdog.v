`include "memory_map.vh"

module watchdog (
    input wire clk,
    input wire rst,
    input wire valid,
    input wire wen,
    input wire [7:0] addr,
    input wire [31:0] wdata,
    input wire payload_active,
    input wire success,
    output reg [31:0] rdata,
    output wire enabled,
    output wire armed,
    output reg timeout,
    output reg [31:0] counter,
    output reg [31:0] limit,
    output reg [31:0] payload_base,
    output reg [31:0] payload_end
);
    localparam REG_CTRL    = 8'h00;
    localparam REG_LIMIT   = 8'h04;
    localparam REG_COUNTER = 8'h08;
    localparam REG_STATUS  = 8'h0c;
    localparam REG_BASE    = 8'h10;
    localparam REG_END     = 8'h14;

    reg ctrl_enabled;
    reg ctrl_armed;

    assign enabled = ctrl_enabled;
    assign armed = ctrl_armed;

    always @(posedge clk) begin
        if (rst) begin
            ctrl_enabled <= 1'b0;
            ctrl_armed <= 1'b0;
            timeout <= 1'b0;
            counter <= 32'h0000_0000;
            limit <= 32'h0010_0000;
            payload_base <= `PAYLOAD_BASE;
            payload_end <= `PAYLOAD_END;
        end else begin
            timeout <= 1'b0;

            if (valid && wen) begin
                case (addr)
                    REG_CTRL: begin
                        ctrl_enabled <= wdata[0];
                        ctrl_armed <= wdata[1];
                        if (wdata[2]) counter <= 32'h0000_0000;
                    end
                    REG_LIMIT: limit <= wdata;
                    REG_COUNTER: counter <= wdata;
                    REG_BASE: payload_base <= wdata;
                    REG_END: payload_end <= wdata;
                    default: begin end
                endcase
            end

            if (success) begin
                ctrl_armed <= 1'b0;
            end else if (payload_active && ctrl_armed && ctrl_enabled) begin
                if (counter >= limit) begin
                    timeout <= 1'b1;
                    ctrl_armed <= 1'b0;
                end else begin
                    counter <= counter + 32'h0000_0001;
                end
            end
        end
    end

    always @(*) begin
        case (addr)
            REG_CTRL: rdata = {30'h0, ctrl_armed, ctrl_enabled};
            REG_LIMIT: rdata = limit;
            REG_COUNTER: rdata = counter;
            REG_STATUS: rdata = {29'h0, timeout, ctrl_armed, ctrl_enabled};
            REG_BASE: rdata = payload_base;
            REG_END: rdata = payload_end;
            default: rdata = 32'h0000_0000;
        endcase
    end
endmodule
