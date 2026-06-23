`timescale 1ns/1ps
`include "memory_map.vh"

module tb_peripherals;
    reg clk = 1'b0;
    reg rst = 1'b1;

    reg uart_valid = 1'b0;
    reg uart_wen = 1'b0;
    reg [7:0] uart_addr = 8'h00;
    reg [31:0] uart_wdata = 32'h0000_0000;
    wire [31:0] uart_rdata;
    wire uart_tx_strobe;
    wire [7:0] uart_tx_data;
    wire uart_rx_consume;
    reg uart_tx_ready = 1'b1;

    reg led_valid = 1'b0;
    reg led_wen = 1'b0;
    reg [7:0] led_addr = 8'h00;
    reg [31:0] led_wdata = 32'h0000_0000;
    wire [31:0] led_rdata;
    wire [7:0] leds;

    reg watchdog_valid = 1'b0;
    reg watchdog_wen = 1'b0;
    reg [7:0] watchdog_addr = 8'h00;
    reg [31:0] watchdog_wdata = 32'h0000_0000;
    wire [31:0] watchdog_rdata;
    wire watchdog_enabled;
    wire watchdog_armed;
    wire watchdog_timeout;
    wire [31:0] watchdog_counter;
    wire [31:0] watchdog_limit;
    wire [31:0] watchdog_payload_base;
    wire [31:0] watchdog_payload_end;

    reg flag_valid = 1'b0;
    reg flag_wen = 1'b0;
    reg [7:0] flag_addr = 8'h00;
    reg [31:0] flag_wdata = 32'h0000_0000;
    wire [31:0] flag_rdata;
    integer tx_i;
    integer tx_j;

    always #5 clk = ~clk;

    uart_mmio uart_i (
        .clk(clk),
        .rst(rst),
        .valid(uart_valid),
        .wen(uart_wen),
        .addr(uart_addr),
        .wdata(uart_wdata),
        .rdata(uart_rdata),
        .tx_strobe(uart_tx_strobe),
        .tx_data(uart_tx_data),
        .tx_ready(uart_tx_ready),
        .rx_valid(1'b0),
        .rx_data(8'h00),
        .rx_consume(uart_rx_consume)
    );

    led_mmio led_i (
        .clk(clk),
        .rst(rst),
        .valid(led_valid),
        .wen(led_wen),
        .addr(led_addr),
        .wdata(led_wdata),
        .rdata(led_rdata),
        .leds(leds)
    );

    watchdog watchdog_i (
        .clk(clk),
        .rst(rst),
        .valid(watchdog_valid),
        .wen(watchdog_wen),
        .addr(watchdog_addr),
        .wdata(watchdog_wdata),
        .payload_active(1'b1),
        .success(1'b0),
        .rdata(watchdog_rdata),
        .enabled(watchdog_enabled),
        .armed(watchdog_armed),
        .timeout(watchdog_timeout),
        .counter(watchdog_counter),
        .limit(watchdog_limit),
        .payload_base(watchdog_payload_base),
        .payload_end(watchdog_payload_end)
    );

    flag_rom flag_rom_i (
        .clk(clk),
        .rst(rst),
        .valid(flag_valid),
        .wen(flag_wen),
        .addr(flag_addr),
        .wdata(flag_wdata),
        .rdata(flag_rdata)
    );

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

    task uart_read;
        input [7:0] a;
        begin
            @(negedge clk);
            uart_addr = a;
            uart_wdata = 32'h0000_0000;
            uart_wen = 1'b0;
            uart_valid = 1'b1;
            @(negedge clk);
            uart_valid = 1'b0;
        end
    endtask

    task uart_write;
        input [7:0] a;
        input [31:0] d;
        begin
            @(negedge clk);
            uart_addr = a;
            uart_wdata = d;
            uart_wen = 1'b1;
            uart_valid = 1'b1;
            @(negedge clk);
            uart_valid = 1'b0;
            uart_wen = 1'b0;
        end
    endtask

    task led_write;
        input [31:0] d;
        begin
            @(negedge clk);
            led_addr = 8'h00;
            led_wdata = d;
            led_wen = 1'b1;
            led_valid = 1'b1;
            @(negedge clk);
            led_valid = 1'b0;
            led_wen = 1'b0;
        end
    endtask

    task watchdog_write;
        input [7:0] a;
        input [31:0] d;
        begin
            @(negedge clk);
            watchdog_addr = a;
            watchdog_wdata = d;
            watchdog_wen = 1'b1;
            watchdog_valid = 1'b1;
            @(negedge clk);
            watchdog_valid = 1'b0;
            watchdog_wen = 1'b0;
        end
    endtask

    task flag_read;
        input [7:0] a;
        begin
            @(negedge clk);
            flag_addr = a;
            flag_wen = 1'b0;
            flag_valid = 1'b1;
            @(negedge clk);
            flag_valid = 1'b0;
        end
    endtask

    task flag_write;
        input [7:0] a;
        input [31:0] d;
        begin
            @(negedge clk);
            flag_addr = a;
            flag_wdata = d;
            flag_wen = 1'b1;
            flag_valid = 1'b1;
            @(negedge clk);
            flag_valid = 1'b0;
            flag_wen = 1'b0;
        end
    endtask

    initial begin
        repeat (3) @(negedge clk);
        rst = 1'b0;

        expect(leds == 8'h00, "LED reset value");
        led_write(32'h0000_005a);
        expect(leds == 8'h5a, "LED write latches");

        uart_tx_ready = 1'b0;
        uart_write(8'h00, 32'h0000_0033);
        expect(uart_tx_strobe == 1'b0, "UART does not drain while downstream not ready");
        uart_read(8'h04);
        expect(uart_rdata[0] == 1'b1, "UART TX_READY reports FIFO space");
        uart_tx_ready = 1'b1;
        @(negedge clk);
        expect(uart_tx_strobe == 1'b1, "UART strobe on TX FIFO drain");
        expect(uart_tx_data == 8'h33, "UART TX data latch");
        @(negedge clk);

        uart_tx_ready = 1'b0;
        for (tx_i = 0; tx_i < 32; tx_i = tx_i + 1) begin
            uart_write(8'h00, {24'h0, tx_i[7:0]});
        end
        uart_read(8'h04);
        expect(uart_rdata[0] == 1'b0, "UART TX_READY clears when FIFO full");
        uart_write(8'h00, 32'h0000_00ff);
        uart_tx_ready = 1'b1;
        for (tx_j = 0; tx_j < 32; tx_j = tx_j + 1) begin
            @(negedge clk);
            expect(uart_tx_strobe == 1'b1, "UART FIFO drains queued byte");
            expect(uart_tx_data == tx_j[7:0], "UART FIFO preserves byte order");
        end
        @(negedge clk);
        expect(uart_tx_strobe == 1'b0, "UART FIFO drops write while full");
        uart_read(8'h04);
        expect(uart_rdata[0] == 1'b1, "UART TX_READY returns after drain");

        expect(watchdog_enabled == 1'b0, "watchdog disabled after reset");
        watchdog_write(8'h04, 32'h0000_0002);
        watchdog_write(8'h00, 32'h0000_0007);
        repeat (5) @(negedge clk);
        expect(watchdog_timeout == 1'b1 || watchdog_armed == 1'b0, "watchdog timeout or disarm");

        flag_read(8'h00);
        expect(flag_rdata == 32'h7965_7267, "flag word 0 grey");
        flag_read(8'h04);
        expect(flag_rdata == 32'h696d_6d7b, "flag word 1 {mmi");
        flag_read(8'h08);
        expect(flag_rdata == 32'h7566_5f6f, "flag word 2 o_fu");
        flag_read(8'h0c);
        expect(flag_rdata == 32'h7d7a_7a7a, "flag word 3 zzz}");
        flag_read(8'h10);
        expect(flag_rdata == 32'h0000_0000, "flag out-of-range data zero");
        flag_read(8'hf0);
        expect(flag_rdata == 32'd16, "flag length metadata");
        flag_read(8'hf4);
        expect(flag_rdata == 32'h0000_0001, "flag status present");
        flag_read(8'hf8);
        expect(flag_rdata == 32'h0000_0000, "flag public profile");
        flag_write(8'h00, 32'hffff_ffff);
        flag_read(8'h00);
        expect(flag_rdata == 32'h7965_7267, "flag ROM ignores writes");

        $display("PASS: tb_peripherals");
        $finish;
    end
endmodule
