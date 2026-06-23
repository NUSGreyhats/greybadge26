`timescale 1ns/1ps

module tb_uart_upload_watchdog;
    parameter EXPECT_TIMEOUT = 1;
    parameter EXPECT_REGION = 0;
    parameter [7:0] EXPECT_LED = 8'hd1;

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
    reg saw_watchdog_reset = 1'b0;
    reg saw_region_reset = 1'b0;
    integer watchdog_match = 0;
    integer region_match = 0;

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
            if ((watchdog_match == 0 && uart_tx_data == "W") ||
                (watchdog_match == 1 && uart_tx_data == "A") ||
                (watchdog_match == 2 && uart_tx_data == "T") ||
                (watchdog_match == 3 && uart_tx_data == "C") ||
                (watchdog_match == 4 && uart_tx_data == "H") ||
                (watchdog_match == 5 && uart_tx_data == "D") ||
                (watchdog_match == 6 && uart_tx_data == "O") ||
                (watchdog_match == 7 && uart_tx_data == "G") ||
                (watchdog_match == 8 && uart_tx_data == "_") ||
                (watchdog_match == 9 && uart_tx_data == "R") ||
                (watchdog_match == 10 && uart_tx_data == "E") ||
                (watchdog_match == 11 && uart_tx_data == "S") ||
                (watchdog_match == 12 && uart_tx_data == "E") ||
                (watchdog_match == 13 && uart_tx_data == "T") ||
                (watchdog_match == 14 && uart_tx_data == "\n")) begin
                watchdog_match <= watchdog_match + 1;
            end else if (uart_tx_data == "W") begin
                watchdog_match <= 1;
            end else begin
                watchdog_match <= 0;
            end

            if (watchdog_match == 14 && uart_tx_data == "\n") begin
                saw_watchdog_reset <= 1'b1;
            end

            if ((region_match == 0 && uart_tx_data == "R") ||
                (region_match == 1 && uart_tx_data == "E") ||
                (region_match == 2 && uart_tx_data == "G") ||
                (region_match == 3 && uart_tx_data == "I") ||
                (region_match == 4 && uart_tx_data == "O") ||
                (region_match == 5 && uart_tx_data == "N") ||
                (region_match == 6 && uart_tx_data == "_") ||
                (region_match == 7 && uart_tx_data == "R") ||
                (region_match == 8 && uart_tx_data == "E") ||
                (region_match == 9 && uart_tx_data == "S") ||
                (region_match == 10 && uart_tx_data == "E") ||
                (region_match == 11 && uart_tx_data == "T") ||
                (region_match == 12 && uart_tx_data == "\n")) begin
                region_match <= region_match + 1;
            end else if (uart_tx_data == "R") begin
                region_match <= 1;
            end else begin
                region_match <= 0;
            end

            if (region_match == 12 && uart_tx_data == "\n") begin
                saw_region_reset <= 1'b1;
            end
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
            $display("FAIL: UPLOAD_HEX plusarg required");
            $finish;
        end

        fd = $fopen(upload_hex_path, "r");
        if (fd == 0) begin
            $display("FAIL: could not open upload hex");
            $finish;
        end

        upload_len = 0;
        while (!$feof(fd)) begin
            code = $fscanf(fd, "%h\n", upload_bytes[upload_len]);
            if (code == 1) upload_len = upload_len + 1;
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

        if (EXPECT_TIMEOUT) begin
            cycles = 0;
            while (cycles < 500000 && !saw_watchdog_reset) begin
                @(posedge clk);
                cycles = cycles + 1;
            end
            if (!saw_watchdog_reset) begin
                $display("\nFAIL: WATCHDOG_RESET not reported");
                $finish;
            end
        end else if (EXPECT_REGION) begin
            cycles = 0;
            while (cycles < 500000 && !saw_region_reset) begin
                @(posedge clk);
                cycles = cycles + 1;
            end
            if (!saw_region_reset) begin
                $display("\nFAIL: REGION_RESET not reported");
                $finish;
            end
            if (saw_watchdog_reset) begin
                $display("\nFAIL: watchdog reset reported during region test");
                $finish;
            end
        end else begin
            cycles = 0;
            while (cycles < 500000 && leds !== EXPECT_LED) begin
                @(posedge clk);
                cycles = cycles + 1;
            end
            if (leds !== EXPECT_LED) begin
                $display("\nFAIL: watchdog disable payload did not set LED %02x", EXPECT_LED);
                $finish;
            end
            if (saw_watchdog_reset) begin
                $display("\nFAIL: watchdog reset reported despite disable payload");
                $finish;
            end
        end

        $display("\nPASS: tb_uart_upload_watchdog");
        $finish;
    end
endmodule
