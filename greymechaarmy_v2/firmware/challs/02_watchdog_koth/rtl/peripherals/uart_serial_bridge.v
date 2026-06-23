module uart_serial_bridge #(
    parameter integer CLKS_PER_BIT = 4036
) (
    input wire clk,
    input wire rst,
    input wire tx_strobe,
    input wire [7:0] tx_data,
    output wire tx_ready,
    output reg serial_tx,
    input wire serial_rx,
    output reg rx_valid,
    output reg [7:0] rx_data
);
    localparam TX_IDLE = 2'd0;
    localparam TX_START = 2'd1;
    localparam TX_DATA = 2'd2;
    localparam TX_STOP = 2'd3;

    localparam RX_IDLE = 2'd0;
    localparam RX_START = 2'd1;
    localparam RX_DATA = 2'd2;
    localparam RX_STOP = 2'd3;

    reg [1:0] tx_state;
    reg [15:0] tx_clk_count;
    reg [2:0] tx_bit_index;
    reg [7:0] tx_shift;

    reg [1:0] rx_state;
    reg [15:0] rx_clk_count;
    reg [3:0] rx_tick_count;
    reg [2:0] rx_bit_index;
    reg [7:0] rx_shift;
    reg [1:0] rx_sync;
    wire rx_sample_tick = rx_clk_count == ((CLKS_PER_BIT / 16) - 1);

    assign tx_ready = (tx_state == TX_IDLE) && !tx_strobe;

    always @(posedge clk) begin
        if (rst) begin
            tx_state <= TX_IDLE;
            tx_clk_count <= 16'd0;
            tx_bit_index <= 3'd0;
            tx_shift <= 8'h00;
            serial_tx <= 1'b1;
        end else begin
            case (tx_state)
                TX_IDLE: begin
                    serial_tx <= 1'b1;
                    tx_clk_count <= 16'd0;
                    tx_bit_index <= 3'd0;
                    if (tx_strobe) begin
                        tx_shift <= tx_data;
                        tx_state <= TX_START;
                    end
                end

                TX_START: begin
                    serial_tx <= 1'b0;
                    if (tx_clk_count == CLKS_PER_BIT - 1) begin
                        tx_clk_count <= 16'd0;
                        tx_state <= TX_DATA;
                    end else begin
                        tx_clk_count <= tx_clk_count + 16'd1;
                    end
                end

                TX_DATA: begin
                    serial_tx <= tx_shift[tx_bit_index];
                    if (tx_clk_count == CLKS_PER_BIT - 1) begin
                        tx_clk_count <= 16'd0;
                        if (tx_bit_index == 3'd7) begin
                            tx_bit_index <= 3'd0;
                            tx_state <= TX_STOP;
                        end else begin
                            tx_bit_index <= tx_bit_index + 3'd1;
                        end
                    end else begin
                        tx_clk_count <= tx_clk_count + 16'd1;
                    end
                end

                TX_STOP: begin
                    serial_tx <= 1'b1;
                    if (tx_clk_count == CLKS_PER_BIT - 1) begin
                        tx_clk_count <= 16'd0;
                        tx_state <= TX_IDLE;
                    end else begin
                        tx_clk_count <= tx_clk_count + 16'd1;
                    end
                end

                default: begin
                    tx_state <= TX_IDLE;
                    serial_tx <= 1'b1;
                end
            endcase
        end
    end

    always @(posedge clk) begin
        if (rst) begin
            rx_state <= RX_IDLE;
            rx_clk_count <= 16'd0;
            rx_tick_count <= 4'd0;
            rx_bit_index <= 3'd0;
            rx_shift <= 8'h00;
            rx_data <= 8'h00;
            rx_valid <= 1'b0;
            rx_sync <= 2'b11;
        end else begin
            rx_valid <= 1'b0;
            rx_sync <= {rx_sync[0], serial_rx};

            case (rx_state)
                RX_IDLE: begin
                    rx_clk_count <= 16'd0;
                    rx_tick_count <= 4'd0;
                    rx_bit_index <= 3'd0;
                    if (rx_sync[1] == 1'b0) begin
                        rx_state <= RX_START;
                    end
                end

                RX_START: begin
                    if (rx_sample_tick) begin
                        rx_clk_count <= 16'd0;
                        if (rx_tick_count == 4'd7) begin
                            if (rx_sync[1] == 1'b0) begin
                                rx_tick_count <= 4'd0;
                                rx_state <= RX_DATA;
                            end else begin
                                rx_tick_count <= 4'd0;
                                rx_state <= RX_IDLE;
                            end
                        end else begin
                            rx_tick_count <= rx_tick_count + 4'd1;
                        end
                    end else begin
                        rx_clk_count <= rx_clk_count + 16'd1;
                    end
                end

                RX_DATA: begin
                    if (rx_sample_tick) begin
                        rx_clk_count <= 16'd0;
                        if (rx_tick_count == 4'd15) begin
                            rx_tick_count <= 4'd0;
                            rx_shift[rx_bit_index] <= rx_sync[1];
                            if (rx_bit_index == 3'd7) begin
                                rx_bit_index <= 3'd0;
                                rx_state <= RX_STOP;
                            end else begin
                                rx_bit_index <= rx_bit_index + 3'd1;
                            end
                        end else begin
                            rx_tick_count <= rx_tick_count + 4'd1;
                        end
                    end else begin
                        rx_clk_count <= rx_clk_count + 16'd1;
                    end
                end

                RX_STOP: begin
                    if (rx_sample_tick) begin
                        rx_clk_count <= 16'd0;
                        if (rx_tick_count == 4'd15) begin
                            rx_tick_count <= 4'd0;
                            if (rx_sync[1] == 1'b1) begin
                                rx_data <= rx_shift;
                                rx_valid <= 1'b1;
                            end
                            rx_state <= RX_IDLE;
                        end else begin
                            rx_tick_count <= rx_tick_count + 4'd1;
                        end
                    end else begin
                        rx_clk_count <= rx_clk_count + 16'd1;
                    end
                end

                default: begin
                    rx_state <= RX_IDLE;
                end
            endcase
        end
    end
endmodule
