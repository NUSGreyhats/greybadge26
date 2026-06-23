module greymecha_smoke_top (
    input wire clk_ext,
    input wire [4:0] btn,
    output wire [7:0] led,
    inout wire [7:0] interconnect,
    inout wire [7:0] pmod_j1,
    inout wire [7:0] pmod_j2,
    inout wire [4:0] s
);
    wire clk_int;
    defparam OSCI1.DIV = "8";
    OSCG OSCI1 (.OSC(clk_int));

    wire clk = clk_int;
    wire unused_clk_ext = clk_ext;
    wire [4:0] unused_btn = btn;

    reg [1:0] reset_sync = 2'b11;
    reg [7:0] reset_counter = 8'h00;
    wire reset_request = reset_sync[1];
    wire resetn = &reset_counter;
    wire rst = !resetn;

    wire [31:0] unused_rdata;
    wire unused_ready;
    wire unused_fault;
    wire uart_tx_strobe;
    wire [7:0] uart_tx_data;
    wire uart_tx_ready;
    wire uart_phy_tx;
    wire uart_rx_valid;
    wire [7:0] uart_rx_data;
    wire display_write_strobe;
    wire display_is_command;
    wire [7:0] display_write_data;
    wire spi_sclk;
    wire spi_mosi;
    wire spi_cs_n;
    wire spi_dc;
    wire spi_rst_n;
    wire [7:0] debug_status;

    wire unused_display_write_strobe = display_write_strobe;
    wire unused_display_is_command = display_is_command;
    wire [7:0] unused_display_write_data = display_write_data;
    wire unused_spi_sclk = spi_sclk;
    wire unused_spi_mosi = spi_mosi;
    wire unused_spi_cs_n = spi_cs_n;
    wire unused_spi_dc = spi_dc;
    wire unused_spi_rst_n = spi_rst_n;

    always @(posedge clk) begin
        reset_sync <= {reset_sync[0], 1'b0};
        if (reset_request) begin
            reset_counter <= 8'h00;
        end else if (!resetn) begin
            reset_counter <= reset_counter + 8'h01;
        end
    end

    watchdog_koth_top soc_i (
        .clk(clk),
        .rst(rst),
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
        .uart_tx_ready(uart_tx_ready),
        .uart_rx_valid(uart_rx_valid),
        .uart_rx_data(uart_rx_data),
        .display_write_strobe(display_write_strobe),
        .display_is_command(display_is_command),
        .display_write_data(display_write_data),
        .spi_sclk(spi_sclk),
        .spi_mosi(spi_mosi),
        .spi_cs_n(spi_cs_n),
        .spi_dc(spi_dc),
        .spi_rst_n(spi_rst_n),
        .debug_status(debug_status)
    );

    uart_serial_bridge #(
        .CLKS_PER_BIT(4036)
    ) uart_phy_i (
        .clk(clk),
        .rst(rst),
        .tx_strobe(uart_tx_strobe),
        .tx_data(uart_tx_data),
        .tx_ready(uart_tx_ready),
        .serial_tx(uart_phy_tx),
        .serial_rx(interconnect[0]),
        .rx_valid(uart_rx_valid),
        .rx_data(uart_rx_data)
    );

    assign interconnect[1] = uart_phy_tx;
    assign interconnect[7:2] = 6'bz;
    assign pmod_j1 = 8'bz;
    assign pmod_j2 = 8'bz;
    assign s = 5'bz;
endmodule
