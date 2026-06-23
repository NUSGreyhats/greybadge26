module greymecha_uart_echo_top (
    input wire clk_ext,
    input wire [4:0] btn,
    output reg [7:0] led,
    inout wire [7:0] interconnect,
    inout wire [7:0] pmod_j1,
    inout wire [7:0] pmod_j2,
    inout wire [4:0] s
);
    wire clk_int;
    defparam OSCI1.DIV = "8";
    OSCG OSCI1 (.OSC(clk_int));

    wire clk = clk_int;
    wire unused_clk_ext = clk_ext;
    wire [4:0] unused_btn = btn;

    reg [7:0] reset_counter = 8'h00;
    wire rst = !(&reset_counter);

    wire tx_ready;
    wire serial_tx;
    wire rx_valid;
    wire [7:0] rx_data;
    reg tx_strobe = 1'b0;
    reg [7:0] tx_data = 8'h00;

    always @(posedge clk) begin
        if (rst) begin
            reset_counter <= reset_counter + 8'd1;
            led <= 8'h00;
            tx_strobe <= 1'b0;
            tx_data <= 8'h00;
        end else begin
            tx_strobe <= 1'b0;
            if (rx_valid && tx_ready) begin
                led <= rx_data;
                tx_data <= rx_data;
                tx_strobe <= 1'b1;
            end
        end
    end

    uart_serial_bridge #(
        .CLKS_PER_BIT(4036)
    ) uart_phy_i (
        .clk(clk),
        .rst(rst),
        .tx_strobe(tx_strobe),
        .tx_data(tx_data),
        .tx_ready(tx_ready),
        .serial_tx(serial_tx),
        .serial_rx(interconnect[0]),
        .rx_valid(rx_valid),
        .rx_data(rx_data)
    );

    assign interconnect[1] = serial_tx;
    assign interconnect[7:2] = 6'bz;
    assign pmod_j1 = 8'bz;
    assign pmod_j2 = 8'bz;
    assign s = 5'bz;
endmodule
