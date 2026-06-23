`timescale 1ns/1ps

module tb_uart_upload_led;
    reg clk = 1'b0;
    reg rst = 1'b1;
    reg uart_rx_valid = 1'b0;
    reg [7:0] uart_rx_data = 8'h00;
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

    reg [7:0] upload_bytes [0:4095];
    integer upload_len = 0;
    integer i;
    integer cycles;
    integer fd;
    integer code;
    reg [1023:0] upload_hex_path;
    reg [31:0] expected_led;

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

    always @(posedge clk) begin
        if (uart_tx_strobe) begin
            $write("%c", uart_tx_data);
        end
    end

    task wait_rx_empty;
        begin
            while (dut.bus_i.uart_i.rx_full !== 1'b0) begin
                @(posedge clk);
            end
        end
    endtask

    task send_byte;
        input [7:0] value;
        begin
            wait_rx_empty();
            @(negedge clk);
            uart_rx_data = value;
            uart_rx_valid = 1'b1;
            @(negedge clk);
            uart_rx_valid = 1'b0;
            uart_rx_data = 8'h00;
        end
    endtask

    initial begin
        if (!$value$plusargs("UPLOAD_HEX=%s", upload_hex_path)) begin
            upload_hex_path = "build/payloads/starter_led/starter_led.wdog.hex";
        end
        if (!$value$plusargs("EXPECT_LED=%h", expected_led)) begin
            expected_led = 32'h0000_005a;
        end

        fd = $fopen(upload_hex_path, "r");
        if (fd == 0) begin
            $display("FAIL: could not open upload hex");
            $finish;
        end

        upload_len = 0;
        while (!$feof(fd)) begin
            code = $fscanf(fd, "%h\n", upload_bytes[upload_len]);
            if (code == 1) begin
                upload_len = upload_len + 1;
            end
        end
        $fclose(fd);

        repeat (10) @(posedge clk);
        rst = 1'b0;

        cycles = 0;
        while (cycles < 200000 && leds !== 8'ha5) begin
            @(posedge clk);
            cycles = cycles + 1;
        end

        if (leds !== 8'ha5) begin
            $display("\nFAIL: firmware selftest LED pattern not observed");
            $finish;
        end

        for (i = 0; i < upload_len; i = i + 1) begin
            send_byte(upload_bytes[i]);
        end

        cycles = 0;
        while (cycles < 300000 && leds !== expected_led[7:0]) begin
            @(posedge clk);
            cycles = cycles + 1;
        end

        if (leds !== expected_led[7:0]) begin
            $display("\nFAIL: uploaded C payload did not set expected LED %02x, got %02x", expected_led[7:0], leds);
            $finish;
        end

        $display("\nPASS: tb_uart_upload_led");
        $finish;
    end
endmodule
