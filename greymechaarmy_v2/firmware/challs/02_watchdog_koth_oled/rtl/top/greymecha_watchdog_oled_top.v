module greymecha_watchdog_oled_top (
    input wire clk_ext,
    input wire [4:0] btn,
    input wire [1:0] btn_mecha,
    output wire [7:0] led,
    inout wire [7:0] interconnect,
    inout wire [7:0] pmod_j1,
    inout wire [7:0] pmod_j2,
    output wire oled_scl,
    output wire oled_sda,
    output wire oled_dc,
    output wire oled_cs,
    output wire oled_rst,
    inout wire [4:0] s
);
    wire oled_osc_clk;
    defparam OLED_OSC.DIV = "6";
    OSCG OLED_OSC (.OSC(oled_osc_clk));

    wire cpu_clk;
    wire oled_clk;
    wire pll_locked;
    ecp5_oled_pll oled_pll_i (
        .clki(oled_osc_clk),
        .clko(oled_clk),
        .clko_cpu(cpu_clk),
        .locked(pll_locked)
    );

    wire unused_clk_ext = clk_ext;
    wire [4:0] unused_btn = btn;
    wire [1:0] unused_btn_mecha = btn_mecha;

    reg [1:0] cpu_reset_sync = 2'b11;
    reg [7:0] cpu_reset_counter = 8'h00;
    wire cpu_reset_request = cpu_reset_sync[1];
    wire cpu_resetn = &cpu_reset_counter;
    wire cpu_rst = !cpu_resetn;

    always @(posedge cpu_clk) begin
        cpu_reset_sync <= {cpu_reset_sync[0], 1'b0};
        if (cpu_reset_request) begin
            cpu_reset_counter <= 8'h00;
        end else if (!cpu_resetn) begin
            cpu_reset_counter <= cpu_reset_counter + 8'h01;
        end
    end

    reg [7:0] oled_reset_counter = 8'h00;
    wire oled_resetn = (&oled_reset_counter) && pll_locked;
    always @(posedge oled_clk) begin
        if (!pll_locked) begin
            oled_reset_counter <= 8'h00;
        end else if (!(&oled_reset_counter)) begin
            oled_reset_counter <= oled_reset_counter + 8'h01;
        end
    end

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
    wire [7:0] debug_status;
    wire fetch_trace_valid;
    wire [31:0] fetch_trace_addr;
    wire [31:0] fetch_trace_instr;
    wire watchdog_trace_enabled;
    wire watchdog_trace_armed;

    wire unused_display_write_strobe = display_write_strobe;
    wire unused_display_is_command = display_is_command;
    wire [7:0] unused_display_write_data = display_write_data;
    wire [7:0] unused_debug_status = debug_status;

    watchdog_koth_oled_soc soc_i (
        .clk(cpu_clk),
        .rst(cpu_rst),
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
        .debug_status(debug_status),
        .fetch_trace_valid(fetch_trace_valid),
        .fetch_trace_addr(fetch_trace_addr),
        .fetch_trace_instr(fetch_trace_instr),
        .watchdog_trace_enabled(watchdog_trace_enabled),
        .watchdog_trace_armed(watchdog_trace_armed)
    );

    uart_serial_bridge #(
        .CLKS_PER_BIT(4036)
    ) uart_phy_i (
        .clk(cpu_clk),
        .rst(cpu_rst),
        .tx_strobe(uart_tx_strobe),
        .tx_data(uart_tx_data),
        .tx_ready(uart_tx_ready),
        .serial_tx(uart_phy_tx),
        .serial_rx(interconnect[0]),
        .rx_valid(uart_rx_valid),
        .rx_data(uart_rx_data)
    );

    wire oled_fetch_valid;
    wire [31:0] oled_fetch_addr;
    wire [31:0] oled_fetch_instr;
    cpu_fetch_cdc fetch_cdc_i (
        .src_clk(cpu_clk),
        .src_rst(cpu_rst),
        .fetch_valid(fetch_trace_valid),
        .fetch_addr(fetch_trace_addr),
        .fetch_instr(fetch_trace_instr),
        .dst_clk(oled_clk),
        .dst_rst(!oled_resetn),
        .event_valid(oled_fetch_valid),
        .event_addr(oled_fetch_addr),
        .event_instr(oled_fetch_instr)
    );

    reg watchdog_enabled_sync_0 = 1'b0;
    reg watchdog_enabled_sync_1 = 1'b0;
    reg watchdog_armed_sync_0 = 1'b0;
    reg watchdog_armed_sync_1 = 1'b0;
    always @(posedge oled_clk) begin
        if (!oled_resetn) begin
            watchdog_enabled_sync_0 <= 1'b0;
            watchdog_enabled_sync_1 <= 1'b0;
            watchdog_armed_sync_0 <= 1'b0;
            watchdog_armed_sync_1 <= 1'b0;
        end else begin
            watchdog_enabled_sync_0 <= watchdog_trace_enabled;
            watchdog_enabled_sync_1 <= watchdog_enabled_sync_0;
            watchdog_armed_sync_0 <= watchdog_trace_armed;
            watchdog_armed_sync_1 <= watchdog_armed_sync_0;
        end
    end

    wire [15:0] pixel_index;
    wire [15:0] pixel_data;
    wire [7:0] heatmap_debug_bucket;
    wire [3:0] heatmap_debug_intensity;
    cpu_heatmap_pixels heatmap_i (
        .clk(oled_clk),
        .rst(!oled_resetn),
        .fetch_valid(oled_fetch_valid),
        .fetch_addr(oled_fetch_addr),
        .watchdog_enabled(watchdog_enabled_sync_1),
        .watchdog_armed(watchdog_armed_sync_1),
        .pixel_index(pixel_index),
        .pixel_data(pixel_data),
        .debug_bucket(heatmap_debug_bucket),
        .debug_intensity(heatmap_debug_intensity)
    );

    wire init_done;
    wire streaming;
    oled_gc9a01 #(
        .CLK_HZ(75000000),
        .INIT_SPI_CLK_DIV(8'd4)
    ) oled_i (
        .clk(oled_clk),
        .resetn(oled_resetn),
        .pixel_index(pixel_index),
        .pixel_data(pixel_data),
        .oled_scl(oled_scl),
        .oled_sda(oled_sda),
        .oled_dc(oled_dc),
        .oled_cs(oled_cs),
        .oled_rst(oled_rst),
        .init_done(init_done),
        .streaming(streaming)
    );

    wire unused_init_done = init_done;
    wire unused_streaming = streaming;
    wire [7:0] unused_heatmap_debug_bucket = heatmap_debug_bucket;
    wire [3:0] unused_heatmap_debug_intensity = heatmap_debug_intensity;

    assign interconnect[1] = uart_phy_tx;
    assign interconnect[7:2] = 6'bz;
    assign pmod_j1 = 8'bz;
    assign pmod_j2 = 8'bz;
    assign s = 5'bz;
endmodule
