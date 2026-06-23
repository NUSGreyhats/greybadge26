module uart_model (
    input wire clk,
    input wire rst,
    input wire tx_strobe,
    input wire [7:0] tx_data,
    output reg [7:0] last_tx,
    output reg [15:0] tx_count
);
    always @(posedge clk) begin
        if (rst) begin
            last_tx <= 8'h00;
            tx_count <= 16'h0000;
        end else if (tx_strobe) begin
            last_tx <= tx_data;
            tx_count <= tx_count + 16'h0001;
        end
    end
endmodule
