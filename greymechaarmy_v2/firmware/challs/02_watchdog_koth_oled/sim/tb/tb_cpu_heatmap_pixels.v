`timescale 1ns/1ps

module tb_cpu_heatmap_pixels;
    reg clk = 1'b0;
    reg rst = 1'b1;
    reg fetch_valid = 1'b0;
    reg [31:0] fetch_addr = 32'h0000_0000;
    reg watchdog_enabled = 1'b0;
    reg watchdog_armed = 1'b0;
    reg [15:0] pixel_index = 16'd0;
    integer p;
    integer current_pixel_index = 0;
    wire [15:0] pixel_data;
    wire [7:0] debug_bucket;
    wire [3:0] debug_intensity;

    always #5 clk = ~clk;

    cpu_heatmap_pixels dut (
        .clk(clk),
        .rst(rst),
        .fetch_valid(fetch_valid),
        .fetch_addr(fetch_addr),
        .watchdog_enabled(watchdog_enabled),
        .watchdog_armed(watchdog_armed),
        .pixel_index(pixel_index),
        .pixel_data(pixel_data),
        .debug_bucket(debug_bucket),
        .debug_intensity(debug_intensity)
    );

    task pulse_fetch;
        input [31:0] addr;
        begin
            @(negedge clk);
            fetch_addr = addr;
            fetch_valid = 1'b1;
            @(negedge clk);
            fetch_valid = 1'b0;
        end
    endtask

    task sample_pixel;
        input [7:0] x;
        input [7:0] y;
        integer target_pixel_index;
        begin
            target_pixel_index = (y * 240) + x;
            if (target_pixel_index < current_pixel_index) begin
                pixel_index = 16'd0;
                current_pixel_index = 0;
                repeat (2) @(posedge clk);
            end
            while (current_pixel_index < target_pixel_index) begin
                current_pixel_index = current_pixel_index + 1;
                pixel_index = current_pixel_index[15:0];
                repeat (2) @(posedge clk);
            end
            repeat (5) @(posedge clk);
        end
    endtask

    initial begin
        repeat (4) @(posedge clk);
        rst = 1'b0;

        pulse_fetch(32'h0000_80a4);
        pulse_fetch(32'h0000_80a8);
        pulse_fetch(32'h0000_80ac);

        repeat (4) @(posedge clk);
        if (debug_bucket !== 8'h0a) begin
            $display("FAIL: expected payload fetch bucket 0a, got %02x", debug_bucket);
            $finish;
        end
        if (debug_intensity < 4'd3) begin
            $display("FAIL: expected bucket intensity >= 3, got %0d", debug_intensity);
            $finish;
        end

        sample_pixel(8'd8, 8'd8);
        if (pixel_data !== 16'h0000) begin
            $display("FAIL: circular unsafe corner should be black, got %04x", pixel_data);
            $finish;
        end

        sample_pixel(8'd104, 8'd20);
        if (pixel_data === 16'h0000) begin
            $display("FAIL: WDOG label pixel should not be black at scan %0d,%0d pixel=%04x",
                     dut.scan_x, dut.scan_y, pixel_data);
            $finish;
        end

        sample_pixel(8'd112, 8'd82);
        if (pixel_data === 16'h0000) begin
            $display("FAIL: PC label pixel should not be black");
            $finish;
        end

        sample_pixel(8'd89, 8'd96);
        if (pixel_data === 16'h0000) begin
            $display("FAIL: PC hex digit pixel should not be black");
            $finish;
        end

        sample_pixel(8'd104, 8'd154);
        if (pixel_data === 16'h0000) begin
            $display("FAIL: HEAT label pixel should not be black");
            $finish;
        end

        sample_pixel(8'd126, 8'd198);
        if (pixel_data === 16'h0000) begin
            $display("FAIL: hot mini heatmap bucket pixel should not be black");
            $finish;
        end

        watchdog_enabled = 1'b0;
        watchdog_armed = 1'b0;
        sample_pixel(8'd120, 8'd52);
        if (pixel_data !== 16'hf800) begin
            $display("FAIL: disabled watchdog indicator should be red, got %04x", pixel_data);
            $finish;
        end

        watchdog_enabled = 1'b1;
        watchdog_armed = 1'b0;
        sample_pixel(8'd120, 8'd52);
        if (pixel_data !== 16'hfd20) begin
            $display("FAIL: enabled-only watchdog indicator should be amber, got %04x", pixel_data);
            $finish;
        end

        watchdog_enabled = 1'b1;
        watchdog_armed = 1'b1;
        sample_pixel(8'd120, 8'd52);
        if (pixel_data !== 16'h07e0) begin
            $display("FAIL: armed watchdog indicator should be green, got %04x", pixel_data);
            $finish;
        end

        $display("PASS: tb_cpu_heatmap_pixels");
        $finish;
    end
endmodule
