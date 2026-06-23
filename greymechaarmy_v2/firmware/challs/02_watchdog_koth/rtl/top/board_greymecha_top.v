module board_greymecha_top (
    input wire clk,
    input wire rst_btn,
    output wire [7:0] led,
    output wire uart_tx,
    input wire uart_rx,
    output wire display_write_strobe,
    output wire display_is_command,
    output wire [7:0] display_write_data,
    output wire oled_scl,
    output wire oled_sda,
    output wire oled_dc,
    output wire oled_cs,
    output wire oled_rst
);
    wire [31:0] unused_rdata;
    wire unused_ready;
    wire unused_fault;
    wire uart_tx_strobe;
    wire [7:0] uart_tx_data;
    wire [7:0] debug_status;
    wire [7:0] unused_debug_status = debug_status;

    watchdog_koth_top soc (
        .clk(clk),
        .rst(rst_btn),
        .cpu_enable(1'b1),
        .bus_valid(1'b0),
        .bus_wstrb(4'b0000),
        .bus_addr(32'h0000_0000),
        .bus_wdata(32'h0000_0000),
        .bus_rdata(unused_rdata),
        .bus_ready(unused_ready),
        .bus_fault(unused_fault),
        .leds(led),
        .uart_tx_strobe(uart_tx_strobe),
        .uart_tx_data(uart_tx_data),
        .uart_tx_ready(1'b1),
        .uart_rx_valid(1'b0),
        .uart_rx_data({7'h00, uart_rx}),
        .display_write_strobe(display_write_strobe),
        .display_is_command(display_is_command),
        .display_write_data(display_write_data),
        .spi_sclk(oled_scl),
        .spi_mosi(oled_sda),
        .spi_cs_n(oled_cs),
        .spi_dc(oled_dc),
        .spi_rst_n(oled_rst),
        .debug_status(debug_status)
    );

    assign uart_tx = uart_tx_strobe ? uart_tx_data[0] : 1'b1;
endmodule
