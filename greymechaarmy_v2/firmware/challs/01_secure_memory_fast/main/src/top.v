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
    assign pmod_j2 = {chall_fast_secmem_value[1], chall_fast_secmem_value[6:2], 1'b0, chall_fast_secmem_value[0]};
    
endmodule
