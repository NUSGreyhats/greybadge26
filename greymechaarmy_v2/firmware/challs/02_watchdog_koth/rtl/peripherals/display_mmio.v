module display_mmio (
    input wire clk,
    input wire rst,
    input wire valid,
    input wire wen,
    input wire [7:0] addr,
    input wire [31:0] wdata,
    output reg [31:0] rdata,
    output reg write_strobe,
    output reg is_command,
    output reg [7:0] write_data,
    output wire spi_sclk,
    output wire spi_mosi,
    output wire spi_cs_n,
    output wire spi_dc,
    output wire spi_rst_n
);
    localparam REG_COMMAND = 8'h00;
    localparam REG_DATA    = 8'h04;
    localparam REG_STATUS  = 8'h08;
    localparam REG_CTRL    = 8'h0c;

    reg [15:0] write_count;
    reg [7:0] spi_tx_latch;
    reg [7:0] spi_clk_div;
    reg spi_keep_cs;
    reg spi_dc_reg;
    reg spi_rst_n_reg;
    reg spi_idle_cs_n;
    reg spi_start;
    reg spi_release_cs;
    wire spi_busy;
    wire spi_done;
    reg spi_done_latch;

    simple_spi_master spi_i (
        .clk(clk),
        .resetn(!rst),
        .clk_div(spi_clk_div),
        .tx_data(spi_tx_latch),
        .start(spi_start),
        .release_cs(spi_release_cs),
        .keep_cs(spi_keep_cs),
        .idle_cs_n(spi_idle_cs_n),
        .dc_in(spi_dc_reg),
        .rst_n_in(spi_rst_n_reg),
        .busy(spi_busy),
        .done(spi_done),
        .sclk(spi_sclk),
        .mosi(spi_mosi),
        .cs_n(spi_cs_n),
        .dc(spi_dc),
        .rst_n(spi_rst_n)
    );

    always @(posedge clk) begin
        if (rst) begin
            write_strobe <= 1'b0;
            is_command <= 1'b0;
            write_data <= 8'h00;
            write_count <= 16'h0000;
            spi_tx_latch <= 8'h00;
            spi_clk_div <= 8'd3;
            spi_keep_cs <= 1'b0;
            spi_dc_reg <= 1'b0;
            spi_rst_n_reg <= 1'b1;
            spi_idle_cs_n <= 1'b1;
            spi_start <= 1'b0;
            spi_release_cs <= 1'b0;
            spi_done_latch <= 1'b0;
        end else begin
            write_strobe <= 1'b0;
            spi_start <= 1'b0;
            spi_release_cs <= 1'b0;

            if (valid && wen && (addr == REG_COMMAND || addr == REG_DATA)) begin
                write_strobe <= 1'b1;
                is_command <= (addr == REG_COMMAND);
                write_data <= wdata[7:0];
                spi_tx_latch <= wdata[7:0];
                spi_dc_reg <= (addr == REG_DATA);
                spi_start <= !spi_busy;
                write_count <= write_count + 16'h0001;
            end

            if (valid && wen && addr == REG_CTRL) begin
                spi_clk_div <= wdata[7:0];
                spi_keep_cs <= wdata[9];
                spi_dc_reg <= wdata[10];
                spi_rst_n_reg <= wdata[11];
                spi_idle_cs_n <= wdata[12];
                spi_release_cs <= wdata[13];
            end

            if (valid && !wen && addr == REG_STATUS) begin
                spi_done_latch <= 1'b0;
            end else if (spi_done) begin
                spi_done_latch <= 1'b1;
            end
        end
    end

    always @(*) begin
        case (addr)
            REG_COMMAND: rdata = {24'h0, write_data};
            REG_DATA: rdata = {24'h0, write_data};
            REG_STATUS: rdata = {13'h0, spi_done_latch | spi_done, spi_busy, write_strobe, write_count};
            REG_CTRL: rdata = {19'h0, spi_idle_cs_n, spi_rst_n_reg, spi_dc_reg, spi_keep_cs, 1'b0, spi_clk_div};
            default: rdata = 32'h0000_0000;
        endcase
    end
endmodule
