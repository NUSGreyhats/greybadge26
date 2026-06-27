// Code your design here
module fast_regular_synchronous_memory(input clk, input [4:0] address, output reg [7:0] value);
	// memory retrieval
	always @ (posedge clk) begin
		value <= (
			address == 5'd0 ? "g" :
			address == 5'd1 ? "r" :
			address == 5'd2 ? "e" :
			address == 5'd3 ? "y" :
			address == 5'd4 ? "{" :
			address == 5'd5 ? "f" :
			address == 5'd6 ? "a" :
			address == 5'd7 ? "s" :
			address == 5'd8 ? "t" :
			address == 5'd9 ? "t" :
			address == 5'd10 ? "i" :
			address == 5'd11 ? "m" :
			address == 5'd12 ? "i" :
			address == 5'd13 ? "n" :
			address == 5'd14 ? "}" :
			address == 5'd31 ? "L" :
			0
		);
	end
endmodule

// I need to make it secure oh shit
module fast_secure_memory(input clk, input [4:0] address, output [7:0] value);
	wire [4:0] mem_address;
	wire [7:0] mem_value;
	fast_regular_synchronous_memory mem (clk, mem_address, mem_value);

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


    /// Chall: Fun SecureMemory /////////////////////////////////////////////////////
    reg chall_fast_secmem_clk = 0; // ~51.67 MHz from the internal oscillator
    always @ (posedge clk) begin
        chall_fast_secmem_clk <= ~chall_fast_secmem_clk;
    end
    wire [4:0] chall_fast_secmem_address;
    wire [7:0] chall_fast_secmem_value;
    fast_secure_memory chall_fast_secmem(
        .clk(chall_fast_secmem_clk), 
        .address(chall_fast_secmem_address), 
        .value(chall_fast_secmem_value)
    );


    wire [4:0] btn_out = btn;
    assign led = (8'b11111111); 

    assign chall_fast_secmem_address = address;
    // PMOD J2 bit 1 is not observable on this badge, so mirror value[1] onto
    // connected PMOD J2 bit 7. Challenge bytes are ASCII, so value[7] is zero.
    // assign pmod_j2 = {chall_fast_secmem_value[7], chall_fast_secmem_value[6:2], chall_fast_secmem_value[1], chall_fast_secmem_value[0]};
    assign pmod_j2 = {chall_fast_secmem_value[1], chall_fast_secmem_value[6:2], chall_fast_secmem_value[1], chall_fast_secmem_value[0]};
    
endmodule
