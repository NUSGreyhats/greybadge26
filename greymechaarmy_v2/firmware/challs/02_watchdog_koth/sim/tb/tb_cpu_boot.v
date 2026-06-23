`timescale 1ns/1ps

module tb_cpu_boot;
    reg clk = 1'b0;
    reg rst = 1'b1;
    wire [31:0] bus_rdata;
    wire bus_ready;
    wire bus_fault;
    wire [7:0] leds;
    wire uart_tx_strobe;
    wire [7:0] uart_tx_data;
    wire display_write_strobe;
    wire display_is_command;
    wire [7:0] display_write_data;
    wire spi_sclk;
    wire spi_mosi;
    wire spi_cs_n;
    wire spi_dc;
    wire spi_rst_n;
    wire [7:0] debug_status;

    reg [8*64-1:0] uart_window = 0;
    integer cycles = 0;

    always #5 clk = ~clk;

    watchdog_koth_top dut (
        .clk(clk),
        .rst(rst),
        .cpu_enable(1'b1),
        .bus_valid(1'b0),
        .bus_wstrb(4'b0000),
        .bus_addr(32'h0000_0000),
        .bus_wdata(32'h0000_0000),
        .bus_rdata(bus_rdata),
        .bus_ready(bus_ready),
        .bus_fault(bus_fault),
        .leds(leds),
        .uart_tx_strobe(uart_tx_strobe),
        .uart_tx_data(uart_tx_data),
        .uart_tx_ready(1'b1),
        .uart_rx_valid(1'b0),
        .uart_rx_data(8'h00),
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

    function has_selftest_ok;
        input [8*64-1:0] window;
        begin
            has_selftest_ok = 0
                || window[8*1 +: 88] == "SELFTEST_OK"
                || window[8*2 +: 88] == "SELFTEST_OK"
                || window[8*3 +: 88] == "SELFTEST_OK"
                || window[8*4 +: 88] == "SELFTEST_OK"
                || window[8*5 +: 88] == "SELFTEST_OK"
                || window[8*6 +: 88] == "SELFTEST_OK"
                || window[8*7 +: 88] == "SELFTEST_OK"
                || window[8*8 +: 88] == "SELFTEST_OK"
                || window[8*9 +: 88] == "SELFTEST_OK"
                || window[8*10 +: 88] == "SELFTEST_OK"
                || window[8*11 +: 88] == "SELFTEST_OK"
                || window[8*12 +: 88] == "SELFTEST_OK"
                || window[8*13 +: 88] == "SELFTEST_OK"
                || window[8*14 +: 88] == "SELFTEST_OK"
                || window[8*15 +: 88] == "SELFTEST_OK";
        end
    endfunction

    function has_ready;
        input [8*64-1:0] window;
        begin
            has_ready = 0
                || window[8*1 +: 40] == "READY"
                || window[8*2 +: 40] == "READY"
                || window[8*3 +: 40] == "READY"
                || window[8*4 +: 40] == "READY"
                || window[8*5 +: 40] == "READY"
                || window[8*6 +: 40] == "READY"
                || window[8*7 +: 40] == "READY"
                || window[8*8 +: 40] == "READY"
                || window[8*9 +: 40] == "READY"
                || window[8*10 +: 40] == "READY"
                || window[8*11 +: 40] == "READY"
                || window[8*12 +: 40] == "READY"
                || window[8*13 +: 40] == "READY"
                || window[8*14 +: 40] == "READY"
                || window[8*15 +: 40] == "READY";
        end
    endfunction

    always @(posedge clk) begin
        if (uart_tx_strobe) begin
            uart_window <= {uart_window[8*63-1:0], uart_tx_data};
            $write("%c", uart_tx_data);
        end
    end

    initial begin
        repeat (10) @(posedge clk);
        rst = 1'b0;

        while (cycles < 200000) begin
            @(posedge clk);
            cycles = cycles + 1;
            if (has_selftest_ok(uart_window) && has_ready(uart_window)) begin
                $display("\nPASS: tb_cpu_boot");
                $finish;
            end
        end

        $display("\nFAIL: CPU boot did not emit SELFTEST_OK and READY");
        $finish;
    end
endmodule
