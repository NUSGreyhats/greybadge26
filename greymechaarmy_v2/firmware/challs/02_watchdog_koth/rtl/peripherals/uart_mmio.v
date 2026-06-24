module uart_mmio (
    input wire clk,
    input wire rst,
    input wire valid,
    input wire wen,
    input wire [7:0] addr,
    input wire [31:0] wdata,
    output reg [31:0] rdata,
    output reg tx_strobe,
    output reg [7:0] tx_data,
    input wire tx_ready,
    input wire rx_valid,
    input wire [7:0] rx_data,
    output reg rx_consume
);
    localparam REG_TXDATA = 8'h00;
    localparam REG_STATUS = 8'h04;
    localparam REG_RXDATA = 8'h08;

    reg [7:0] tx_fifo [0:31];
    reg [4:0] tx_rd_ptr;
    reg [4:0] tx_wr_ptr;
    reg [5:0] tx_count;
    wire tx_fifo_empty = tx_count == 6'd0;
    wire tx_fifo_full = tx_count == 6'd32;
    wire tx_fifo_space = !tx_fifo_full;
    wire tx_write = valid && wen && addr == REG_TXDATA && tx_fifo_space;
    wire tx_drain = tx_ready && !tx_fifo_empty;

    reg [7:0] rx_fifo [0:15];
    reg [3:0] rx_rd_ptr;
    reg [3:0] rx_wr_ptr;
    reg [4:0] rx_count;
    wire rx_full = (rx_count != 5'd0);
    wire rx_fifo_full = rx_count == 5'd16;
    wire rx_read = valid && !wen && addr == REG_RXDATA && rx_full;

    always @(posedge clk) begin
        if (rst) begin
            tx_strobe <= 1'b0;
            tx_data <= 8'h00;
            tx_rd_ptr <= 5'd0;
            tx_wr_ptr <= 5'd0;
            tx_count <= 6'd0;
            rx_rd_ptr <= 4'd0;
            rx_wr_ptr <= 4'd0;
            rx_count <= 5'd0;
            rx_consume <= 1'b0;
        end else begin
            tx_strobe <= 1'b0;
            rx_consume <= 1'b0;

            if (tx_drain) begin
                tx_data <= tx_fifo[tx_rd_ptr];
                tx_strobe <= 1'b1;
                tx_rd_ptr <= tx_rd_ptr + 5'd1;
            end

            if (tx_write) begin
                tx_fifo[tx_wr_ptr] <= wdata[7:0];
                tx_wr_ptr <= tx_wr_ptr + 5'd1;
            end

            case ({tx_write, tx_drain})
                2'b10: tx_count <= tx_count + 6'd1;
                2'b01: tx_count <= tx_count - 6'd1;
                default: tx_count <= tx_count;
            endcase

            if (rx_valid && !rx_fifo_full) begin
                rx_fifo[rx_wr_ptr] <= rx_data;
                rx_wr_ptr <= rx_wr_ptr + 4'd1;
            end

            if (rx_read) begin
                rx_rd_ptr <= rx_rd_ptr + 4'd1;
                rx_consume <= 1'b1;
            end

            case ({rx_valid && !rx_fifo_full, rx_read})
                2'b10: rx_count <= rx_count + 5'd1;
                2'b01: rx_count <= rx_count - 5'd1;
                default: rx_count <= rx_count;
            endcase
        end
    end

    always @(*) begin
        case (addr)
            REG_TXDATA: rdata = {24'h0, tx_data};
            REG_STATUS: rdata = {29'h0, tx_fifo_empty, rx_full, tx_fifo_space};
            REG_RXDATA: rdata = {24'h0, rx_fifo[rx_rd_ptr]};
            default: rdata = 32'h0000_0000;
        endcase
    end
endmodule
