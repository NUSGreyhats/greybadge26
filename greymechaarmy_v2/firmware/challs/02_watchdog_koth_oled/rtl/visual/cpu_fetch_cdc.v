module cpu_fetch_cdc (
    input wire src_clk,
    input wire src_rst,
    input wire fetch_valid,
    input wire [31:0] fetch_addr,
    input wire [31:0] fetch_instr,
    input wire dst_clk,
    input wire dst_rst,
    output reg event_valid,
    output reg [31:0] event_addr,
    output reg [31:0] event_instr
);
    reg req_toggle = 1'b0;
    reg ack_toggle = 1'b0;
    reg [31:0] hold_addr = 32'h0000_0000;
    reg [31:0] hold_instr = 32'h0000_0000;

    reg ack_sync_0 = 1'b0;
    reg ack_sync_1 = 1'b0;
    reg req_sync_0 = 1'b0;
    reg req_sync_1 = 1'b0;
    reg req_seen = 1'b0;

    wire src_idle = (ack_sync_1 == req_toggle);

    always @(posedge src_clk) begin
        if (src_rst) begin
            req_toggle <= 1'b0;
            hold_addr <= 32'h0000_0000;
            hold_instr <= 32'h0000_0000;
            ack_sync_0 <= 1'b0;
            ack_sync_1 <= 1'b0;
        end else begin
            ack_sync_0 <= ack_toggle;
            ack_sync_1 <= ack_sync_0;
            if (fetch_valid && src_idle) begin
                hold_addr <= fetch_addr;
                hold_instr <= fetch_instr;
                req_toggle <= ~req_toggle;
            end
        end
    end

    always @(posedge dst_clk) begin
        if (dst_rst) begin
            req_sync_0 <= 1'b0;
            req_sync_1 <= 1'b0;
            req_seen <= 1'b0;
            ack_toggle <= 1'b0;
            event_valid <= 1'b0;
            event_addr <= 32'h0000_0000;
            event_instr <= 32'h0000_0000;
        end else begin
            event_valid <= 1'b0;
            req_sync_0 <= req_toggle;
            req_sync_1 <= req_sync_0;
            if (req_sync_1 != req_seen) begin
                event_addr <= hold_addr;
                event_instr <= hold_instr;
                event_valid <= 1'b1;
                req_seen <= req_sync_1;
                ack_toggle <= req_sync_1;
            end
        end
    end
endmodule
