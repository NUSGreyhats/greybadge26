module display_sink (
    input wire clk,
    input wire rst,
    input wire write_strobe,
    input wire is_command,
    input wire [7:0] write_data,
    output reg [7:0] last_data,
    output reg last_is_command,
    output reg [15:0] write_count
);
    always @(posedge clk) begin
        if (rst) begin
            last_data <= 8'h00;
            last_is_command <= 1'b0;
            write_count <= 16'h0000;
        end else if (write_strobe) begin
            last_data <= write_data;
            last_is_command <= is_command;
            write_count <= write_count + 16'h0001;
        end
    end
endmodule
