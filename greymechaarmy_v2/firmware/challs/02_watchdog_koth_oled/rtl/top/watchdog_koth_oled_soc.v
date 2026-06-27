`include "memory_map.vh"

module watchdog_koth_oled_soc (
    input wire clk,
    input wire rst,
    input wire cpu_enable,
    input wire bus_valid,
    input wire [3:0] bus_wstrb,
    input wire [31:0] bus_addr,
    input wire [31:0] bus_wdata,
    output wire [31:0] bus_rdata,
    output wire bus_ready,
    output wire bus_fault,
    output wire [7:0] leds,
    output wire uart_tx_strobe,
    output wire [7:0] uart_tx_data,
    input wire uart_tx_ready,
    input wire uart_rx_valid,
    input wire [7:0] uart_rx_data,
    output wire display_write_strobe,
    output wire display_is_command,
    output wire [7:0] display_write_data,
    output wire [7:0] debug_status,
    output wire fetch_trace_valid,
    output wire [31:0] fetch_trace_addr,
    output wire [31:0] fetch_trace_instr,
    output wire watchdog_trace_enabled,
    output wire watchdog_trace_armed
);
    wire cpu_mem_valid;
    wire cpu_mem_instr;
    wire cpu_mem_ready;
    wire [31:0] cpu_mem_addr;
    wire [31:0] cpu_mem_wdata;
    wire [3:0] cpu_mem_wstrb;
    wire [31:0] cpu_mem_rdata;
    wire watchdog_reset_request;
    wire region_reset_request;
    wire soft_reset_request = watchdog_reset_request || region_reset_request;
    reg [3:0] soft_reset_count = 4'h0;
    wire soft_cpu_reset = soft_reset_count != 4'h0;
    wire [7:0] bus_debug_status;
    reg [63:0] cpu_clock_cycle_count;
    reg passive_watchdog_enabled;
    reg passive_watchdog_armed;

    wire selected_valid = cpu_enable ? cpu_mem_valid : bus_valid;
    wire [3:0] selected_wstrb = cpu_enable ? cpu_mem_wstrb : bus_wstrb;
    wire [31:0] selected_addr = cpu_enable ? cpu_mem_addr : bus_addr;
    wire [31:0] selected_wdata = cpu_enable ? cpu_mem_wdata : bus_wdata;
    wire selected_wen = |selected_wstrb;
    wire selected_watchdog_ctrl_write = selected_valid && bus_ready && selected_wen &&
                                        (selected_addr >= `WATCHDOG_BASE) &&
                                        (selected_addr <= `WATCHDOG_END) &&
                                        (selected_addr[7:0] == 8'h00);

    wire unused_spi_sclk;
    wire unused_spi_mosi;
    wire unused_spi_cs_n;
    wire unused_spi_dc;
    wire unused_spi_rst_n;

    picorv32 #(
        .ENABLE_COUNTERS(0),
        .ENABLE_COUNTERS64(0),
        .ENABLE_REGS_16_31(1),
        .ENABLE_REGS_DUALPORT(1),
        .TWO_STAGE_SHIFT(1),
        .BARREL_SHIFTER(0),
        .COMPRESSED_ISA(0),
        .ENABLE_MUL(0),
        .ENABLE_DIV(0),
        .LATCHED_MEM_RDATA(1),
        .PROGADDR_RESET(32'h0000_0000),
        .STACKADDR(32'h0000_d000)
    ) cpu_i (
        .clk(clk),
        .resetn(!rst && !soft_cpu_reset && cpu_enable),
        .mem_valid(cpu_mem_valid),
        .mem_instr(cpu_mem_instr),
        .mem_ready(cpu_mem_ready),
        .mem_addr(cpu_mem_addr),
        .mem_wdata(cpu_mem_wdata),
        .mem_wstrb(cpu_mem_wstrb),
        .mem_rdata(cpu_mem_rdata)
    );

    soc_bus bus_i (
        .clk(clk),
        .rst(rst),
        .valid(selected_valid),
        .instr_fetch(cpu_enable && cpu_mem_instr),
        .wstrb(selected_wstrb),
        .addr(selected_addr),
        .wdata(selected_wdata),
        .rdata(bus_rdata),
        .ready(bus_ready),
        .fault(bus_fault),
        .leds(leds),
        .uart_tx_strobe(uart_tx_strobe),
        .uart_tx_data(uart_tx_data),
        .uart_tx_ready(uart_tx_ready),
        .uart_rx_valid(uart_rx_valid),
        .uart_rx_data(uart_rx_data),
        .display_write_strobe(display_write_strobe),
        .display_is_command(display_is_command),
        .display_write_data(display_write_data),
        .spi_sclk(unused_spi_sclk),
        .spi_mosi(unused_spi_mosi),
        .spi_cs_n(unused_spi_cs_n),
        .spi_dc(unused_spi_dc),
        .spi_rst_n(unused_spi_rst_n),
        .watchdog_reset_request(watchdog_reset_request),
        .region_reset_request(region_reset_request),
        .cycle_count(cpu_clock_cycle_count),
        .debug_status(bus_debug_status)
    );

    assign cpu_mem_ready = cpu_enable ? bus_ready : 1'b0;
    assign cpu_mem_rdata = bus_rdata;
    assign fetch_trace_valid = cpu_enable && cpu_mem_valid && cpu_mem_instr && cpu_mem_ready;
    assign fetch_trace_addr = cpu_mem_addr;
    assign fetch_trace_instr = cpu_mem_rdata;
    assign watchdog_trace_enabled = passive_watchdog_enabled;
    assign watchdog_trace_armed = passive_watchdog_armed;

    always @(posedge clk) begin
        if (rst) begin
            soft_reset_count <= 4'h0;
            cpu_clock_cycle_count <= 64'h0000_0000_0000_0000;
            passive_watchdog_enabled <= 1'b0;
            passive_watchdog_armed <= 1'b0;
        end else begin
            cpu_clock_cycle_count <= cpu_clock_cycle_count + 64'h0000_0000_0000_0001;
            if (selected_watchdog_ctrl_write) begin
                passive_watchdog_enabled <= selected_wdata[0];
                passive_watchdog_armed <= selected_wdata[1];
            end else if (watchdog_reset_request) begin
                passive_watchdog_armed <= 1'b0;
            end
            if (soft_reset_request) begin
                soft_reset_count <= 4'hf;
            end else if (soft_reset_count != 4'h0) begin
                soft_reset_count <= soft_reset_count - 4'h1;
            end
        end
    end

    assign debug_status = {
        bus_debug_status[6],
        bus_debug_status[5],
        bus_debug_status[4],
        bus_debug_status[2],
        cpu_mem_instr,
        bus_debug_status[1],
        cpu_mem_valid,
        !rst
    };
endmodule
