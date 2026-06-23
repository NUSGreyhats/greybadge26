module top(
    input clk_ext,
    input [4:0] btn,
    output [7:0] led,
    input [1:0] rp_to_fpga,
    output [2:0] fpga_to_rp
);
    assign led = 8'hff;

    // Interconnect split-direction loopback test:
    //   RP GP8  -> FPGA rp_to_fpga[0] -> FPGA fpga_to_rp[1] -> RP GP11
    //   RP GP9  -> FPGA rp_to_fpga[1] -> FPGA fpga_to_rp[2] -> RP GP12
    //   FPGA fpga_to_rp[0] drives high as a sanity marker -> RP GP10
    // GP10-GP12 must be configured as inputs on the RP side.
    assign fpga_to_rp = {rp_to_fpga[1], rp_to_fpga[0], 1'b1};
endmodule
