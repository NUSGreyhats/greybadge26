`include "memory_map.vh"
`ifdef SYNTH_BOOT_PATH_VH
`include "bootloader_path.vh"
`endif

module soc_bus (
    input wire clk,
    input wire rst,
    input wire valid,
    input wire instr_fetch,
    input wire [3:0] wstrb,
    input wire [31:0] addr,
    input wire [31:0] wdata,
    output reg [31:0] rdata,
    output wire ready,
    output reg fault,
    output wire [7:0] leds,
    output wire uart_tx_strobe,
    output wire [7:0] uart_tx_data,
    input wire uart_tx_ready,
    input wire uart_rx_valid,
    input wire [7:0] uart_rx_data,
    output wire display_write_strobe,
    output wire display_is_command,
    output wire [7:0] display_write_data,
    output wire spi_sclk,
    output wire spi_mosi,
    output wire spi_cs_n,
    output wire spi_dc,
    output wire spi_rst_n,
    output wire watchdog_reset_request,
    output wire region_reset_request,
    input wire [63:0] cycle_count,
    output reg [7:0] debug_status
);
    reg ready_reg;
    assign ready = ready_reg;
    wire wen = |wstrb;
    wire accept = valid && !ready_reg;

    wire sel_boot = (addr >= `BOOT_BASE) && (addr <= `BOOT_END);
    wire sel_payload = (addr >= `PAYLOAD_BASE) && (addr <= `PAYLOAD_END);
    wire sel_stack = (addr >= `STACK_BASE) && (addr <= `STACK_END);
    wire sel_uart = (addr >= `UART_BASE) && (addr <= `UART_END);
    wire sel_led = (addr >= `LED_BASE) && (addr <= `LED_END);
    wire sel_watchdog = (addr >= `WATCHDOG_BASE) && (addr <= `WATCHDOG_END);
    wire sel_reset = (addr >= `RESET_STATUS_BASE) && (addr <= `RESET_STATUS_END);
    wire sel_display = (addr >= `DISPLAY_BASE) && (addr <= `DISPLAY_END);
    wire sel_flag = (addr >= `FLAG_BASE) && (addr <= `FLAG_END);

    wire sel_any = sel_boot || sel_payload || sel_stack || sel_uart || sel_led ||
                   sel_watchdog || sel_reset || sel_display || sel_flag;

    reg [31:0] boot_mem [0:8191];
    reg [31:0] payload_mem [0:4095];
    reg [31:0] stack_mem [0:1023];

    wire [31:0] uart_rdata;
    wire [31:0] led_rdata;
    wire [31:0] display_rdata;
    wire [31:0] watchdog_rdata;
    wire [31:0] reset_rdata;
    wire [31:0] flag_rdata;
    wire uart_rx_consume;
    wire watchdog_timeout;
    wire watchdog_enabled;
    wire watchdog_armed;
    wire [31:0] watchdog_counter;
    wire [31:0] watchdog_limit;
    wire [31:0] watchdog_payload_base;
    wire [31:0] watchdog_payload_end;
    wire [31:0] reset_reason_value;
    wire payload_entry_fetch = accept && instr_fetch &&
                               (addr >= watchdog_payload_base) &&
                               (addr <= watchdog_payload_end);
    wire watchdog_enforcement_active = watchdog_enabled && watchdog_armed;
    wire payload_region_violation = watchdog_enforcement_active &&
                                    payload_active && accept && instr_fetch &&
                                    ((addr < watchdog_payload_base) ||
                                     (addr > watchdog_payload_end));
    reg payload_active;

    assign watchdog_reset_request = watchdog_timeout;
    assign region_reset_request = payload_region_violation;

    integer i;
`ifdef SYNTH_BOOT_CASE_VH
`include "boot_rom_case.vh"
`endif

    initial begin
        for (i = 0; i < 8192; i = i + 1) boot_mem[i] = 32'h0000_0000;
        for (i = 0; i < 4096; i = i + 1) payload_mem[i] = 32'h0000_0000;
        for (i = 0; i < 1024; i = i + 1) stack_mem[i] = 32'h0000_0000;
        boot_mem[0] = 32'h0000_006f;
`ifdef BOOT_HEX
        $readmemh(`BOOT_HEX, boot_mem);
`else
`ifdef SYNTH_BOOT_HEX
        $readmemh("build/firmware/bootloader.hex", boot_mem);
`endif
`endif
    end

    uart_mmio uart_i (
        .clk(clk),
        .rst(rst),
        .valid(accept && sel_uart),
        .wen(wen),
        .addr(addr[7:0]),
        .wdata(wdata),
        .rdata(uart_rdata),
        .tx_strobe(uart_tx_strobe),
        .tx_data(uart_tx_data),
        .tx_ready(uart_tx_ready),
        .rx_valid(uart_rx_valid),
        .rx_data(uart_rx_data),
        .rx_consume(uart_rx_consume)
    );

    led_mmio led_i (
        .clk(clk),
        .rst(rst),
        .valid(accept && sel_led),
        .wen(wen),
        .addr(addr[7:0]),
        .wdata(wdata),
        .rdata(led_rdata),
        .leds(leds)
    );

    display_mmio display_i (
        .clk(clk),
        .rst(rst),
        .valid(accept && sel_display),
        .wen(wen),
        .addr(addr[7:0]),
        .wdata(wdata),
        .rdata(display_rdata),
        .write_strobe(display_write_strobe),
        .is_command(display_is_command),
        .write_data(display_write_data),
        .spi_sclk(spi_sclk),
        .spi_mosi(spi_mosi),
        .spi_cs_n(spi_cs_n),
        .spi_dc(spi_dc),
        .spi_rst_n(spi_rst_n)
    );

    watchdog watchdog_i (
        .clk(clk),
        .rst(rst),
        .valid(accept && sel_watchdog),
        .wen(wen),
        .addr(addr[7:0]),
        .wdata(wdata),
        .payload_active(payload_active),
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

    reset_reason reset_reason_i (
        .clk(clk),
        .rst(rst),
        .valid(accept && sel_reset),
        .wen(wen),
        .addr(addr[7:0]),
        .wdata(wdata),
        .set_reason(watchdog_timeout || payload_region_violation),
        .reason_in(payload_region_violation ? `RESET_REGION : `RESET_WATCHDOG),
        .cycle_count(cycle_count),
        .rdata(reset_rdata),
        .reason(reset_reason_value)
    );

    flag_rom flag_rom_i (
        .clk(clk),
        .rst(rst),
        .valid(accept && sel_flag),
        .wen(wen),
        .addr(addr[7:0]),
        .wdata(wdata),
        .rdata(flag_rdata)
    );

    always @(posedge clk) begin
        if (rst) begin
            ready_reg <= 1'b0;
            rdata <= 32'h0000_0000;
            payload_active <= 1'b0;
            debug_status <= 8'h00;
        end else begin
            ready_reg <= 1'b0;
            if (watchdog_timeout || payload_region_violation) begin
                payload_active <= 1'b0;
            end else if (payload_entry_fetch) begin
                payload_active <= 1'b1;
            end
            if (valid) begin
                debug_status[0] <= 1'b1;
            end
            if (accept) begin
                ready_reg <= 1'b1;
                debug_status[1] <= 1'b1;
                if (sel_boot) debug_status[2] <= 1'b1;
                if (sel_payload || sel_stack) debug_status[3] <= 1'b1;
                if (wen && sel_led) debug_status[4] <= 1'b1;
                if (wen && sel_uart) debug_status[5] <= 1'b1;
                if (!sel_any) debug_status[6] <= 1'b1;
                if (wen && sel_payload) begin
                    if (wstrb[0]) payload_mem[(addr - `PAYLOAD_BASE) >> 2][7:0] <= wdata[7:0];
                    if (wstrb[1]) payload_mem[(addr - `PAYLOAD_BASE) >> 2][15:8] <= wdata[15:8];
                    if (wstrb[2]) payload_mem[(addr - `PAYLOAD_BASE) >> 2][23:16] <= wdata[23:16];
                    if (wstrb[3]) payload_mem[(addr - `PAYLOAD_BASE) >> 2][31:24] <= wdata[31:24];
                end
                if (wen && sel_stack) begin
                    if (wstrb[0]) stack_mem[(addr - `STACK_BASE) >> 2][7:0] <= wdata[7:0];
                    if (wstrb[1]) stack_mem[(addr - `STACK_BASE) >> 2][15:8] <= wdata[15:8];
                    if (wstrb[2]) stack_mem[(addr - `STACK_BASE) >> 2][23:16] <= wdata[23:16];
                    if (wstrb[3]) stack_mem[(addr - `STACK_BASE) >> 2][31:24] <= wdata[31:24];
                end

                if (sel_boot) begin
`ifdef SYNTH_BOOT_CASE_VH
                    rdata <= boot_rom_word((addr - `BOOT_BASE) >> 2);
`else
                    rdata <= boot_mem[(addr - `BOOT_BASE) >> 2];
`endif
                end else if (sel_payload) begin
                    rdata <= payload_mem[(addr - `PAYLOAD_BASE) >> 2];
                end else if (sel_stack) begin
                    rdata <= stack_mem[(addr - `STACK_BASE) >> 2];
                end else if (sel_uart) begin
                    rdata <= uart_rdata;
                end else if (sel_led) begin
                    rdata <= led_rdata;
                end else if (sel_watchdog) begin
                    rdata <= watchdog_rdata;
                end else if (sel_reset) begin
                    rdata <= reset_rdata;
                end else if (sel_display) begin
                    rdata <= display_rdata;
                end else if (sel_flag) begin
                    rdata <= flag_rdata;
                end else begin
                    rdata <= `UNMAPPED_RDATA;
                end
            end
        end
    end

    always @(*) begin
        fault = valid && !sel_any;
    end
endmodule
