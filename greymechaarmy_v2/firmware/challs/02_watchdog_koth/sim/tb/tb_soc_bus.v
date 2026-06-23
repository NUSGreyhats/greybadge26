`timescale 1ns/1ps
`include "memory_map.vh"

module tb_soc_bus;
    reg clk = 1'b0;
    reg rst = 1'b1;
    reg valid = 1'b0;
    reg [3:0] wstrb = 4'b0000;
    reg [31:0] addr = 32'h0000_0000;
    reg [31:0] wdata = 32'h0000_0000;
    wire [31:0] rdata;
    wire ready;
    wire fault;
    wire [7:0] leds;
    wire uart_tx_strobe;
    wire [7:0] uart_tx_data;
    reg uart_rx_valid = 1'b0;
    reg [7:0] uart_rx_data = 8'h00;
    wire display_write_strobe;
    wire display_is_command;
    wire [7:0] display_write_data;
    wire spi_sclk;
    wire spi_mosi;
    wire spi_cs_n;
    wire spi_dc;
    wire spi_rst_n;
    wire [7:0] debug_status;

    always #5 clk = ~clk;

    watchdog_koth_top dut (
        .clk(clk),
        .rst(rst),
        .cpu_enable(1'b0),
        .bus_valid(valid),
        .bus_wstrb(wstrb),
        .bus_addr(addr),
        .bus_wdata(wdata),
        .bus_rdata(rdata),
        .bus_ready(ready),
        .bus_fault(fault),
        .leds(leds),
        .uart_tx_strobe(uart_tx_strobe),
        .uart_tx_data(uart_tx_data),
        .uart_tx_ready(1'b1),
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

    task bus_write;
        input [31:0] a;
        input [31:0] d;
        begin
            @(negedge clk);
            addr = a;
            wdata = d;
            wstrb = 4'b1111;
            valid = 1'b1;
            @(negedge clk);
            valid = 1'b0;
            wstrb = 4'b0000;
        end
    endtask

    task bus_read;
        input [31:0] a;
        begin
            @(negedge clk);
            addr = a;
            wdata = 32'h0000_0000;
            wstrb = 4'b0000;
            valid = 1'b1;
            @(negedge clk);
            valid = 1'b0;
        end
    endtask

    task expect;
        input condition;
        input [255:0] message;
        begin
            if (!condition) begin
                $display("FAIL: %0s", message);
                $finish;
            end
        end
    endtask

    initial begin
        repeat (3) @(negedge clk);
        rst = 1'b0;

        bus_read(`BOOT_BASE);
        expect(rdata == 32'h0000_006f, "boot reset vector is deterministic");

        bus_write(`PAYLOAD_BASE, 32'h1234_5678);
        bus_read(`PAYLOAD_BASE);
        expect(rdata == 32'h1234_5678, "payload RAM readback");

        bus_write(`STACK_BASE, 32'ha5a5_5a5a);
        bus_read(`STACK_BASE);
        expect(rdata == 32'ha5a5_5a5a, "stack RAM readback");

        bus_write(`LED_BASE, 32'h0000_00c3);
        bus_read(`LED_BASE);
        expect(rdata == 32'h0000_00c3, "LED MMIO readback");
        expect(leds == 8'hc3, "LED output latched");

        bus_write(`UART_BASE, 32'h0000_0041);
        @(negedge clk);
        expect(uart_tx_strobe == 1'b1, "UART TX strobe");
        expect(uart_tx_data == 8'h41, "UART TX data");

        bus_write(`DISPLAY_BASE, 32'h0000_00aa);
        expect(display_write_strobe == 1'b1, "display write strobe");
        expect(display_is_command == 1'b1, "display command select");
        expect(display_write_data == 8'haa, "display command data");

        bus_write(`WATCHDOG_BASE + 32'h04, 32'h0000_0020);
        bus_read(`WATCHDOG_BASE + 32'h04);
        expect(rdata == 32'h0000_0020, "watchdog limit readback");

        bus_read(`RESET_STATUS_BASE);
        expect(rdata == `RESET_CLEAN_BOOT, "reset reason clean boot");
        bus_read(`RESET_STATUS_BASE + 32'h04);
        expect(rdata != 32'h0000_0000, "cycle low is exposed");
        bus_read(`RESET_STATUS_BASE + 32'h08);
        expect(rdata == 32'h0000_0000, "cycle high is exposed");

        bus_read(`FLAG_BASE);
        expect(rdata == 32'h7965_7267, "flag first word");
        bus_read(`FLAG_BASE + 32'h04);
        expect(rdata == 32'h696d_6d7b, "flag second word");
        bus_read(`FLAG_BASE + 32'hf0);
        expect(rdata == 32'd16, "flag length over SoC bus");
        bus_read(`FLAG_BASE + 32'hf4);
        expect(rdata == 32'h0000_0001, "flag status over SoC bus");
        bus_write(`FLAG_BASE, 32'hffff_ffff);
        bus_read(`FLAG_BASE);
        expect(rdata == 32'h7965_7267, "flag ignores writes over SoC bus");

        bus_read(32'h3000_0000);
        expect(fault == 1'b1, "unmapped read faults");
        expect(rdata == `UNMAPPED_RDATA, "unmapped read data deterministic");

        $display("PASS: tb_soc_bus");
        $finish;
    end
endmodule
