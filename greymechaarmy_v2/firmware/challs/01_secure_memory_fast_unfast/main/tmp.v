// Code your design here
module regular_synchronous_memory(input clk, input [4:0] address, output reg [7:0] value);
	// memory retrieval
	always @ (posedge clk) begin
		value <= (
			address == 5'd0 ? "g" :
			address == 5'd1 ? "r" :
			address == 5'd2 ? "e" :
			address == 5'd3 ? "y" :
			address == 5'd4 ? "{" :
			address == 5'd5 ? "r" :
			address == 5'd6 ? "a" :
			address == 5'd7 ? "c" :
			address == 5'd8 ? "e" :
			address == 5'd9 ? "_" :
			address == 5'd10 ? "f" :
			address == 5'd11 ? "l" :
			address == 5'd12 ? "a" :
			address == 5'd13 ? "g" :
			address == 5'd14 ? "}" :
			address == 5'd31 ? "L" :
			0
		);
	end
endmodule

// I need to make it secure oh shit
module secure_memory(input clk, input [4:0] address, output [7:0] value);
	wire [4:0] mem_address;
	wire [7:0] mem_value;
	regular_synchronous_memory mem (clk, mem_address, mem_value);

	// Haha its secure now
	assign mem_address = address;
    assign value = ( mem_address == 5'd31 ? mem_value : "?" );
endmodule
module top(
    input clk_ext, input [4:0] btn, output [7:0] led, 
    input [4:0] address,
    output [7:0] pmod_j2
);
    /// Internal Configuration ///////////////////////////////////////////
    wire clk_int;        // Internal OSCILLATOR clock
    defparam OSCI1.DIV = "3"; // 50MHz ish
    OSCG OSCI1 (.OSC(clk_int));

    wire clk = clk_int;
    localparam CLK_FREQ = 103_340_000; // EXT CLK

    // External Oscillator Easter egg /////
    reg clk_ext_soldered = 0;
    always @ (posedge clk_ext) begin clk_ext_soldered <= 1; end

    // Clock Configuration
    reg [31:0] clk_stepdown_counter = 0;
    reg [31:0] clk_stepdown_count_val = 5;
    reg clk_stepdown;
    always @ (posedge clk) begin
        clk_stepdown_counter <= clk_stepdown_counter + 1;
        if (clk_stepdown_counter >= clk_stepdown_count_val) begin
            clk_stepdown <= ~clk_stepdown;
            clk_stepdown_counter <= 0;
        end
    end

    // Slow Clock Speed
    reg chall_secmem_clk = 0; // 10hz clock
    reg [31:0] chall_secmem_clk_counter = 0; 
    always @ (posedge clk) begin
        chall_secmem_clk_counter <= chall_secmem_clk_counter + 1;
        if (chall_secmem_clk_counter >= CLK_FREQ/20) begin
            chall_secmem_clk <= ~chall_secmem_clk;
            chall_secmem_clk_counter <= 0;
        end
    end
    wire [4:0] chall_secmem_address;
    wire [7:0] chall_secmem_value;
    secure_memory chall_secmem(
        .clk(chall_secmem_clk), 
        .address(chall_secmem_address), 
        .value(chall_secmem_value)
    );

    wire [4:0] btn_out = btn;
    assign led = (8'b11111111); 

    assign chall_secmem_address = address;
    assign pmod_j2 = chall_secmem_value;
    
endmodule
