module flag_model (
    input wire [7:0] addr,
    output reg [31:0] rdata
);
    always @(*) begin
        case (addr[7:2])
            6'd0: rdata = 32'h7965_7267;
            6'd1: rdata = 32'h696d_6d7b;
            6'd2: rdata = 32'h7566_5f6f;
            6'd3: rdata = 32'h7d7a_7a7a;
            default: rdata = 32'h0000_0000;
        endcase
    end
endmodule
