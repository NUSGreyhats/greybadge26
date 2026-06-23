`timescale 1ns/1ps

module tb_uart_upload_payload;
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

    reg [7:0] upload_bytes [0:65535];
    integer upload_len = 0;
    integer i;
    integer cycles;
    integer fd;
    integer code;
    integer max_cycles;
    reg [1023:0] upload_hex_path;
    reg [31:0] expected_led;
    reg check_led;
    reg expect_watchdog_reset;
    reg expect_region_reset;
    reg expect_return_ready;
    reg has_expectation;
    reg saw_watchdog_reset = 1'b0;
    reg saw_region_reset = 1'b0;
    reg saw_cycle_end = 1'b0;
    reg saw_cycle_delta = 1'b0;
    reg saw_done = 1'b0;
    reg saw_ready_after_done = 1'b0;
    reg uart_line_start = 1'b1;
    integer watchdog_match = 0;
    integer region_match = 0;
    integer cycle_end_match = 0;
    integer cycle_delta_match = 0;
    integer done_match = 0;
    integer ready_match = 0;

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
            if (uart_line_start) begin
                $write("%c[32m[UART %0d]: %c[0m", 8'h1b, dut.cpu_clock_cycle_count, 8'h1b);
            end
            $write("%c", uart_tx_data);
            uart_line_start <= (uart_tx_data == "\n");

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

            if ((cycle_end_match == 0 && uart_tx_data == "C") ||
                (cycle_end_match == 1 && uart_tx_data == "Y") ||
                (cycle_end_match == 2 && uart_tx_data == "C") ||
                (cycle_end_match == 3 && uart_tx_data == "L") ||
                (cycle_end_match == 4 && uart_tx_data == "E") ||
                (cycle_end_match == 5 && uart_tx_data == "_") ||
                (cycle_end_match == 6 && uart_tx_data == "E") ||
                (cycle_end_match == 7 && uart_tx_data == "N") ||
                (cycle_end_match == 8 && uart_tx_data == "D") ||
                (cycle_end_match == 9 && uart_tx_data == " ")) begin
                cycle_end_match <= cycle_end_match + 1;
            end else if (uart_tx_data == "C") begin
                cycle_end_match <= 1;
            end else begin
                cycle_end_match <= 0;
            end
            if (cycle_end_match == 9 && uart_tx_data == " ") begin
                saw_cycle_end <= 1'b1;
            end

            if ((cycle_delta_match == 0 && uart_tx_data == "C") ||
                (cycle_delta_match == 1 && uart_tx_data == "Y") ||
                (cycle_delta_match == 2 && uart_tx_data == "C") ||
                (cycle_delta_match == 3 && uart_tx_data == "L") ||
                (cycle_delta_match == 4 && uart_tx_data == "E") ||
                (cycle_delta_match == 5 && uart_tx_data == "_") ||
                (cycle_delta_match == 6 && uart_tx_data == "D") ||
                (cycle_delta_match == 7 && uart_tx_data == "E") ||
                (cycle_delta_match == 8 && uart_tx_data == "L") ||
                (cycle_delta_match == 9 && uart_tx_data == "T") ||
                (cycle_delta_match == 10 && uart_tx_data == "A") ||
                (cycle_delta_match == 11 && uart_tx_data == " ")) begin
                cycle_delta_match <= cycle_delta_match + 1;
            end else if (uart_tx_data == "C") begin
                cycle_delta_match <= 1;
            end else begin
                cycle_delta_match <= 0;
            end
            if (cycle_delta_match == 11 && uart_tx_data == " ") begin
                saw_cycle_delta <= 1'b1;
            end

            if ((done_match == 0 && uart_tx_data == "D") ||
                (done_match == 1 && uart_tx_data == "O") ||
                (done_match == 2 && uart_tx_data == "N") ||
                (done_match == 3 && uart_tx_data == "E") ||
                (done_match == 4 && uart_tx_data == "\n")) begin
                done_match <= done_match + 1;
            end else if (uart_tx_data == "D") begin
                done_match <= 1;
            end else begin
                done_match <= 0;
            end
            if (done_match == 4 && uart_tx_data == "\n") begin
                saw_done <= 1'b1;
            end

            if ((ready_match == 0 && uart_tx_data == "R") ||
                (ready_match == 1 && uart_tx_data == "E") ||
                (ready_match == 2 && uart_tx_data == "A") ||
                (ready_match == 3 && uart_tx_data == "D") ||
                (ready_match == 4 && uart_tx_data == "Y") ||
                (ready_match == 5 && uart_tx_data == "\n")) begin
                ready_match <= ready_match + 1;
            end else if (uart_tx_data == "R") begin
                ready_match <= 1;
            end else begin
                ready_match <= 0;
            end
            if (saw_done && ready_match == 5 && uart_tx_data == "\n") begin
                saw_ready_after_done <= 1'b1;
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
            $display("[TESTBENCH]: FAIL: UPLOAD_HEX plusarg required");
            $finish;
        end

        check_led = $value$plusargs("EXPECT_LED=%h", expected_led);
        expect_watchdog_reset = $test$plusargs("EXPECT_WATCHDOG_RESET");
        expect_region_reset = $test$plusargs("EXPECT_REGION_RESET");
        expect_return_ready = $test$plusargs("EXPECT_RETURN_READY");
        has_expectation = check_led || expect_watchdog_reset || expect_region_reset || expect_return_ready;
        if (!$value$plusargs("MAX_CYCLES=%d", max_cycles)) begin
            max_cycles = 300000;
        end

        fd = $fopen(upload_hex_path, "r");
        if (fd == 0) begin
            $display("[TESTBENCH]: FAIL: could not open upload hex");
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
            if (!uart_line_start) $write("\n");
            $display("[TESTBENCH]: FAIL: firmware selftest LED pattern not observed");
            $finish;
        end

        for (i = 0; i < upload_len; i = i + 1) begin
            send_byte(upload_bytes[i]);
        end

        cycles = 0;
        while (cycles < max_cycles) begin
            @(posedge clk);
            cycles = cycles + 1;
            if (has_expectation &&
                (!check_led || leds === expected_led[7:0]) &&
                (!expect_watchdog_reset || saw_watchdog_reset) &&
                (!expect_region_reset || saw_region_reset) &&
                (!expect_return_ready || (saw_cycle_end && saw_cycle_delta && saw_done && saw_ready_after_done))) begin
                cycles = max_cycles;
            end
        end

        if (check_led && leds !== expected_led[7:0]) begin
            if (!uart_line_start) $write("\n");
            $display("[TESTBENCH]: FAIL: expected LED %02x, got %02x", expected_led[7:0], leds);
            $finish;
        end
        if (expect_watchdog_reset && !saw_watchdog_reset) begin
            if (!uart_line_start) $write("\n");
            $display("[TESTBENCH]: FAIL: WATCHDOG_RESET not reported");
            $finish;
        end
        if (expect_region_reset && !saw_region_reset) begin
            if (!uart_line_start) $write("\n");
            $display("[TESTBENCH]: FAIL: REGION_RESET not reported");
            $finish;
        end
        if (expect_return_ready && !(saw_cycle_end && saw_cycle_delta && saw_done && saw_ready_after_done)) begin
            if (!uart_line_start) $write("\n");
            $display("[TESTBENCH]: FAIL: returning payload did not report cycle end/delta, DONE, and next READY");
            $finish;
        end
        if (!expect_watchdog_reset && saw_watchdog_reset) begin
            if (!uart_line_start) $write("\n");
            $display("[TESTBENCH]: FAIL: unexpected WATCHDOG_RESET");
            $finish;
        end
        if (!expect_region_reset && saw_region_reset) begin
            if (!uart_line_start) $write("\n");
            $display("[TESTBENCH]: FAIL: unexpected REGION_RESET");
            $finish;
        end

        if (!uart_line_start) $write("\n");
        $display("[TESTBENCH]: PASS: tb_uart_upload_payload");
        $finish;
    end
endmodule
