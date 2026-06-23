`timescale 1ns/1ps

module tb_uart_serial_bridge;
    localparam integer CLKS_PER_BIT = 32;

    reg clk = 1'b0;
    reg rst = 1'b1;
    reg tx_strobe = 1'b0;
    reg [7:0] tx_data = 8'h00;
    wire tx_ready;
    wire serial_tx;
    reg serial_rx = 1'b1;
    wire rx_valid;
    wire [7:0] rx_data;

    always #5 clk = ~clk;

    initial begin
        repeat (2000) @(posedge clk);
        $display("FAIL: tb_uart_serial_bridge timeout");
        $finish;
    end

    uart_serial_bridge #(
        .CLKS_PER_BIT(CLKS_PER_BIT)
    ) dut (
        .clk(clk),
        .rst(rst),
        .tx_strobe(tx_strobe),
        .tx_data(tx_data),
        .tx_ready(tx_ready),
        .serial_tx(serial_tx),
        .serial_rx(serial_rx),
        .rx_valid(rx_valid),
        .rx_data(rx_data)
    );

    task send_serial_byte;
        input [7:0] value;
        integer bit_index;
        begin
            @(negedge clk);
            serial_rx = 1'b0;
            repeat (CLKS_PER_BIT) @(negedge clk);
            for (bit_index = 0; bit_index < 8; bit_index = bit_index + 1) begin
                serial_rx = value[bit_index];
                repeat (CLKS_PER_BIT) @(negedge clk);
            end
            serial_rx = 1'b1;
            repeat (CLKS_PER_BIT) @(negedge clk);
        end
    endtask

    task expect_rx_byte;
        input [7:0] expected;
        integer wait_count;
        begin
            wait_count = 0;
            while (!rx_valid && wait_count < 1000) begin
                wait_count = wait_count + 1;
                @(posedge clk);
            end

            if (!rx_valid) begin
                $display("FAIL: rx_valid timeout for %02x", expected);
                $finish;
            end
            if (rx_data !== expected) begin
                $display("FAIL: rx_data expected %02x got %02x", expected, rx_data);
                $finish;
            end
            @(posedge clk);
        end
    endtask

    task expect_tx_byte;
        input [7:0] expected;
        integer bit_index;
        begin
            wait (serial_tx == 1'b0);
            repeat (CLKS_PER_BIT + (CLKS_PER_BIT / 2)) @(posedge clk);
            for (bit_index = 0; bit_index < 8; bit_index = bit_index + 1) begin
                if (serial_tx !== expected[bit_index]) begin
                    $display("FAIL: tx bit %0d expected %0b got %0b", bit_index, expected[bit_index], serial_tx);
                    $finish;
                end
                repeat (CLKS_PER_BIT) @(posedge clk);
            end
            if (serial_tx !== 1'b1) begin
                $display("FAIL: tx stop bit low");
                $finish;
            end
        end
    endtask

    initial begin
        repeat (4) @(posedge clk);
        rst = 1'b0;
        repeat (4) @(posedge clk);

        fork
            begin
                send_serial_byte(8'h57);
                send_serial_byte(8'ha5);
            end
            begin
                expect_rx_byte(8'h57);
                expect_rx_byte(8'ha5);
            end
        join

        @(posedge clk);
        tx_data = 8'h3c;
        tx_strobe = 1'b1;
        @(posedge clk);
        tx_strobe = 1'b0;
        expect_tx_byte(8'h3c);

        $display("PASS: tb_uart_serial_bridge");
        $finish;
    end
endmodule
