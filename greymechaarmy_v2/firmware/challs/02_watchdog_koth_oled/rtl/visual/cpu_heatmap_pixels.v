module cpu_heatmap_pixels (
    input wire clk,
    input wire rst,
    input wire fetch_valid,
    input wire [31:0] fetch_addr,
    input wire watchdog_enabled,
    input wire watchdog_armed,
    input wire [15:0] pixel_index,
    output reg [15:0] pixel_data,
    output reg [7:0] debug_bucket,
    output wire [3:0] debug_intensity
);
    localparam [15:0] RGB_BLACK = 16'h0000;
    localparam [15:0] RGB_WHITE = 16'hffff;
    localparam [15:0] RGB_GREEN = 16'h07e0;
    localparam [15:0] RGB_AMBER = 16'hfd20;
    localparam [15:0] RGB_RED   = 16'hf800;

    localparam [7:0] CH_0 = 8'h30;
    localparam [7:0] CH_1 = 8'h31;
    localparam [7:0] CH_2 = 8'h32;
    localparam [7:0] CH_3 = 8'h33;
    localparam [7:0] CH_4 = 8'h34;
    localparam [7:0] CH_5 = 8'h35;
    localparam [7:0] CH_6 = 8'h36;
    localparam [7:0] CH_7 = 8'h37;
    localparam [7:0] CH_8 = 8'h38;
    localparam [7:0] CH_9 = 8'h39;
    localparam [7:0] CH_A = 8'h41;
    localparam [7:0] CH_B = 8'h42;
    localparam [7:0] CH_C = 8'h43;
    localparam [7:0] CH_D = 8'h44;
    localparam [7:0] CH_E = 8'h45;
    localparam [7:0] CH_F = 8'h46;
    localparam [7:0] CH_G = 8'h47;
    localparam [7:0] CH_H = 8'h48;
    localparam [7:0] CH_M = 8'h4d;
    localparam [7:0] CH_N = 8'h4e;
    localparam [7:0] CH_O = 8'h4f;
    localparam [7:0] CH_P = 8'h50;
    localparam [7:0] CH_R = 8'h52;
    localparam [7:0] CH_S = 8'h53;
    localparam [7:0] CH_T = 8'h54;
    localparam [7:0] CH_W = 8'h57;

    localparam [2:0] TEXT_TITLE = 3'd0;
    localparam [2:0] TEXT_STATE = 3'd1;
    localparam [2:0] TEXT_EN    = 3'd2;
    localparam [2:0] TEXT_ARM   = 3'd3;
    localparam [2:0] TEXT_PC    = 3'd4;
    localparam [2:0] TEXT_PCV   = 3'd5;
    localparam [2:0] TEXT_HEAT  = 3'd6;

    reg [3:0] buckets [0:15];
    reg [3:0] last_bucket;
    reg [15:0] prev_pixel_index;
    reg [7:0] scan_x;
    reg [7:0] scan_y;
    reg [31:0] current_pc;
    integer i;

    wire [3:0] fetch_bucket = fetch_addr[7:4];
    assign debug_intensity = buckets[last_bucket];

    wire pixel_advanced = pixel_index != prev_pixel_index;
    wire [1:0] mini_cell_x = (scan_x < 8'd108) ? 2'd0 :
                             (scan_x < 8'd120) ? 2'd1 :
                             (scan_x < 8'd132) ? 2'd2 : 2'd3;
    wire [1:0] mini_cell_y = (scan_y < 8'd186) ? 2'd0 :
                             (scan_y < 8'd198) ? 2'd1 :
                             (scan_y < 8'd210) ? 2'd2 : 2'd3;
    wire [3:0] pixel_bucket = {mini_cell_y, mini_cell_x};
    wire [3:0] intensity = buckets[pixel_bucket];

    reg text_hit;
    reg [2:0] text_id;
    reg [3:0] text_chars;
    reg [7:0] text_origin_x;
    reg [7:0] text_origin_y;

    reg s1_text_valid;
    reg [2:0] s1_text_id;
    reg [3:0] s1_char_index;
    reg [2:0] s1_glyph_x;
    reg [2:0] s1_glyph_y;
    reg s1_state_bar;
    reg s1_enable_box;
    reg s1_arm_box;
    reg s1_heatmap_cell;
    reg [3:0] s1_intensity;
    reg s1_watchdog_enabled;
    reg s1_watchdog_armed;

    reg s2_text_pixel;
    reg s2_state_bar;
    reg s2_enable_box;
    reg s2_arm_box;
    reg s2_heatmap_cell;
    reg [3:0] s2_intensity;
    reg s2_watchdog_enabled;
    reg s2_watchdog_armed;

    reg [7:0] rel_x;
    reg [7:0] rel_y;
    reg [7:0] selected_char;
    reg [4:0] selected_row;

    function [15:0] heat_color;
        input [3:0] value;
        begin
            case (value)
                4'h0: heat_color = RGB_BLACK;
                4'h1: heat_color = 16'h0200;
                4'h2: heat_color = 16'h0400;
                4'h3: heat_color = 16'h0600;
                4'h4: heat_color = RGB_GREEN;
                4'h5: heat_color = 16'h27e0;
                4'h6: heat_color = 16'h47e0;
                4'h7: heat_color = 16'h67e0;
                4'h8: heat_color = 16'h87e0;
                4'h9: heat_color = 16'ha7e0;
                4'ha: heat_color = 16'hc7e0;
                4'hb: heat_color = 16'he7e0;
                4'hc: heat_color = 16'hffe0;
                4'hd: heat_color = RGB_AMBER;
                4'he: heat_color = 16'hfa60;
                default: heat_color = RGB_RED;
            endcase
        end
    endfunction

    function [3:0] pc_nibble;
        input [2:0] index;
        begin
            case (index)
                3'd0: pc_nibble = current_pc[31:28];
                3'd1: pc_nibble = current_pc[27:24];
                3'd2: pc_nibble = current_pc[23:20];
                3'd3: pc_nibble = current_pc[19:16];
                3'd4: pc_nibble = current_pc[15:12];
                3'd5: pc_nibble = current_pc[11:8];
                3'd6: pc_nibble = current_pc[7:4];
                default: pc_nibble = current_pc[3:0];
            endcase
        end
    endfunction

    function [7:0] hex_char;
        input [3:0] value;
        begin
            case (value)
                4'h0: hex_char = CH_0;
                4'h1: hex_char = CH_1;
                4'h2: hex_char = CH_2;
                4'h3: hex_char = CH_3;
                4'h4: hex_char = CH_4;
                4'h5: hex_char = CH_5;
                4'h6: hex_char = CH_6;
                4'h7: hex_char = CH_7;
                4'h8: hex_char = CH_8;
                4'h9: hex_char = CH_9;
                4'ha: hex_char = CH_A;
                4'hb: hex_char = CH_B;
                4'hc: hex_char = CH_C;
                4'hd: hex_char = CH_D;
                4'he: hex_char = CH_E;
                default: hex_char = CH_F;
            endcase
        end
    endfunction

    function [7:0] text_char;
        input [2:0] id;
        input [3:0] index;
        begin
            case (id)
                TEXT_TITLE: begin
                    case (index)
                        4'd0: text_char = CH_W;
                        4'd1: text_char = CH_D;
                        4'd2: text_char = CH_O;
                        default: text_char = CH_G;
                    endcase
                end
                TEXT_STATE: begin
                    case (index)
                        4'd0: text_char = CH_S;
                        4'd1: text_char = CH_T;
                        4'd2: text_char = CH_A;
                        4'd3: text_char = CH_T;
                        default: text_char = CH_E;
                    endcase
                end
                TEXT_EN: text_char = (index == 4'd0) ? CH_E : CH_N;
                TEXT_ARM: begin
                    case (index)
                        4'd0: text_char = CH_A;
                        4'd1: text_char = CH_R;
                        default: text_char = CH_M;
                    endcase
                end
                TEXT_PC: text_char = (index == 4'd0) ? CH_P : CH_C;
                TEXT_PCV: text_char = hex_char(pc_nibble(index[2:0]));
                default: begin
                    case (index)
                        4'd0: text_char = CH_H;
                        4'd1: text_char = CH_E;
                        4'd2: text_char = CH_A;
                        default: text_char = CH_T;
                    endcase
                end
            endcase
        end
    endfunction

    function [4:0] glyph_row;
        input [7:0] ch;
        input [2:0] row;
        begin
            case (ch)
                CH_0: case (row) 3'd0: glyph_row = 5'b01110; 3'd1: glyph_row = 5'b10001; 3'd2: glyph_row = 5'b10011; 3'd3: glyph_row = 5'b10101; 3'd4: glyph_row = 5'b11001; 3'd5: glyph_row = 5'b10001; default: glyph_row = 5'b01110; endcase
                CH_1: case (row) 3'd0: glyph_row = 5'b00100; 3'd1: glyph_row = 5'b01100; 3'd2: glyph_row = 5'b00100; 3'd3: glyph_row = 5'b00100; 3'd4: glyph_row = 5'b00100; 3'd5: glyph_row = 5'b00100; default: glyph_row = 5'b01110; endcase
                CH_2: case (row) 3'd0: glyph_row = 5'b01110; 3'd1: glyph_row = 5'b10001; 3'd2: glyph_row = 5'b00001; 3'd3: glyph_row = 5'b00010; 3'd4: glyph_row = 5'b00100; 3'd5: glyph_row = 5'b01000; default: glyph_row = 5'b11111; endcase
                CH_3: case (row) 3'd0: glyph_row = 5'b11110; 3'd1: glyph_row = 5'b00001; 3'd2: glyph_row = 5'b00001; 3'd3: glyph_row = 5'b01110; 3'd4: glyph_row = 5'b00001; 3'd5: glyph_row = 5'b00001; default: glyph_row = 5'b11110; endcase
                CH_4: case (row) 3'd0: glyph_row = 5'b00010; 3'd1: glyph_row = 5'b00110; 3'd2: glyph_row = 5'b01010; 3'd3: glyph_row = 5'b10010; 3'd4: glyph_row = 5'b11111; 3'd5: glyph_row = 5'b00010; default: glyph_row = 5'b00010; endcase
                CH_5: case (row) 3'd0: glyph_row = 5'b11111; 3'd1: glyph_row = 5'b10000; 3'd2: glyph_row = 5'b10000; 3'd3: glyph_row = 5'b11110; 3'd4: glyph_row = 5'b00001; 3'd5: glyph_row = 5'b00001; default: glyph_row = 5'b11110; endcase
                CH_6: case (row) 3'd0: glyph_row = 5'b01110; 3'd1: glyph_row = 5'b10000; 3'd2: glyph_row = 5'b10000; 3'd3: glyph_row = 5'b11110; 3'd4: glyph_row = 5'b10001; 3'd5: glyph_row = 5'b10001; default: glyph_row = 5'b01110; endcase
                CH_7: case (row) 3'd0: glyph_row = 5'b11111; 3'd1: glyph_row = 5'b00001; 3'd2: glyph_row = 5'b00010; 3'd3: glyph_row = 5'b00100; 3'd4: glyph_row = 5'b01000; 3'd5: glyph_row = 5'b01000; default: glyph_row = 5'b01000; endcase
                CH_8: case (row) 3'd0: glyph_row = 5'b01110; 3'd1: glyph_row = 5'b10001; 3'd2: glyph_row = 5'b10001; 3'd3: glyph_row = 5'b01110; 3'd4: glyph_row = 5'b10001; 3'd5: glyph_row = 5'b10001; default: glyph_row = 5'b01110; endcase
                CH_9: case (row) 3'd0: glyph_row = 5'b01110; 3'd1: glyph_row = 5'b10001; 3'd2: glyph_row = 5'b10001; 3'd3: glyph_row = 5'b01111; 3'd4: glyph_row = 5'b00001; 3'd5: glyph_row = 5'b00001; default: glyph_row = 5'b01110; endcase
                CH_A: case (row) 3'd0: glyph_row = 5'b01110; 3'd1: glyph_row = 5'b10001; 3'd2: glyph_row = 5'b10001; 3'd3: glyph_row = 5'b11111; 3'd4: glyph_row = 5'b10001; 3'd5: glyph_row = 5'b10001; default: glyph_row = 5'b10001; endcase
                CH_B: case (row) 3'd0: glyph_row = 5'b11110; 3'd1: glyph_row = 5'b10001; 3'd2: glyph_row = 5'b10001; 3'd3: glyph_row = 5'b11110; 3'd4: glyph_row = 5'b10001; 3'd5: glyph_row = 5'b10001; default: glyph_row = 5'b11110; endcase
                CH_C: case (row) 3'd0: glyph_row = 5'b01111; 3'd1: glyph_row = 5'b10000; 3'd2: glyph_row = 5'b10000; 3'd3: glyph_row = 5'b10000; 3'd4: glyph_row = 5'b10000; 3'd5: glyph_row = 5'b10000; default: glyph_row = 5'b01111; endcase
                CH_D: case (row) 3'd0: glyph_row = 5'b11110; 3'd1: glyph_row = 5'b10001; 3'd2: glyph_row = 5'b10001; 3'd3: glyph_row = 5'b10001; 3'd4: glyph_row = 5'b10001; 3'd5: glyph_row = 5'b10001; default: glyph_row = 5'b11110; endcase
                CH_E: case (row) 3'd0: glyph_row = 5'b11111; 3'd1: glyph_row = 5'b10000; 3'd2: glyph_row = 5'b10000; 3'd3: glyph_row = 5'b11110; 3'd4: glyph_row = 5'b10000; 3'd5: glyph_row = 5'b10000; default: glyph_row = 5'b11111; endcase
                CH_F: case (row) 3'd0: glyph_row = 5'b11111; 3'd1: glyph_row = 5'b10000; 3'd2: glyph_row = 5'b10000; 3'd3: glyph_row = 5'b11110; 3'd4: glyph_row = 5'b10000; 3'd5: glyph_row = 5'b10000; default: glyph_row = 5'b10000; endcase
                CH_G: case (row) 3'd0: glyph_row = 5'b01111; 3'd1: glyph_row = 5'b10000; 3'd2: glyph_row = 5'b10000; 3'd3: glyph_row = 5'b10111; 3'd4: glyph_row = 5'b10001; 3'd5: glyph_row = 5'b10001; default: glyph_row = 5'b01111; endcase
                CH_H: case (row) 3'd0: glyph_row = 5'b10001; 3'd1: glyph_row = 5'b10001; 3'd2: glyph_row = 5'b10001; 3'd3: glyph_row = 5'b11111; 3'd4: glyph_row = 5'b10001; 3'd5: glyph_row = 5'b10001; default: glyph_row = 5'b10001; endcase
                CH_M: case (row) 3'd0: glyph_row = 5'b10001; 3'd1: glyph_row = 5'b11011; 3'd2: glyph_row = 5'b10101; 3'd3: glyph_row = 5'b10101; 3'd4: glyph_row = 5'b10001; 3'd5: glyph_row = 5'b10001; default: glyph_row = 5'b10001; endcase
                CH_N: case (row) 3'd0: glyph_row = 5'b10001; 3'd1: glyph_row = 5'b11001; 3'd2: glyph_row = 5'b10101; 3'd3: glyph_row = 5'b10011; 3'd4: glyph_row = 5'b10001; 3'd5: glyph_row = 5'b10001; default: glyph_row = 5'b10001; endcase
                CH_O: case (row) 3'd0: glyph_row = 5'b01110; 3'd1: glyph_row = 5'b10001; 3'd2: glyph_row = 5'b10001; 3'd3: glyph_row = 5'b10001; 3'd4: glyph_row = 5'b10001; 3'd5: glyph_row = 5'b10001; default: glyph_row = 5'b01110; endcase
                CH_P: case (row) 3'd0: glyph_row = 5'b11110; 3'd1: glyph_row = 5'b10001; 3'd2: glyph_row = 5'b10001; 3'd3: glyph_row = 5'b11110; 3'd4: glyph_row = 5'b10000; 3'd5: glyph_row = 5'b10000; default: glyph_row = 5'b10000; endcase
                CH_R: case (row) 3'd0: glyph_row = 5'b11110; 3'd1: glyph_row = 5'b10001; 3'd2: glyph_row = 5'b10001; 3'd3: glyph_row = 5'b11110; 3'd4: glyph_row = 5'b10100; 3'd5: glyph_row = 5'b10010; default: glyph_row = 5'b10001; endcase
                CH_S: case (row) 3'd0: glyph_row = 5'b01111; 3'd1: glyph_row = 5'b10000; 3'd2: glyph_row = 5'b10000; 3'd3: glyph_row = 5'b01110; 3'd4: glyph_row = 5'b00001; 3'd5: glyph_row = 5'b00001; default: glyph_row = 5'b11110; endcase
                CH_T: case (row) 3'd0: glyph_row = 5'b11111; 3'd1: glyph_row = 5'b00100; 3'd2: glyph_row = 5'b00100; 3'd3: glyph_row = 5'b00100; 3'd4: glyph_row = 5'b00100; 3'd5: glyph_row = 5'b00100; default: glyph_row = 5'b00100; endcase
                CH_W: case (row) 3'd0: glyph_row = 5'b10001; 3'd1: glyph_row = 5'b10001; 3'd2: glyph_row = 5'b10001; 3'd3: glyph_row = 5'b10101; 3'd4: glyph_row = 5'b10101; 3'd5: glyph_row = 5'b11011; default: glyph_row = 5'b10001; endcase
                default: glyph_row = 5'b00000;
            endcase
        end
    endfunction

    always @(*) begin
        text_hit = 1'b0;
        text_id = TEXT_TITLE;
        text_chars = 4'd0;
        text_origin_x = 8'd0;
        text_origin_y = 8'd0;

        if ((scan_y >= 8'd20) && (scan_y < 8'd28) && (scan_x >= 8'd104) && (scan_x < 8'd136)) begin
            text_hit = 1'b1;
            text_id = TEXT_TITLE;
            text_chars = 4'd4;
            text_origin_x = 8'd104;
            text_origin_y = 8'd20;
        end else if ((scan_y >= 8'd36) && (scan_y < 8'd44) && (scan_x >= 8'd100) && (scan_x < 8'd140)) begin
            text_hit = 1'b1;
            text_id = TEXT_STATE;
            text_chars = 4'd5;
            text_origin_x = 8'd100;
            text_origin_y = 8'd36;
        end else if ((scan_y >= 8'd64) && (scan_y < 8'd72) && (scan_x >= 8'd88) && (scan_x < 8'd104)) begin
            text_hit = 1'b1;
            text_id = TEXT_EN;
            text_chars = 4'd2;
            text_origin_x = 8'd88;
            text_origin_y = 8'd64;
        end else if ((scan_y >= 8'd64) && (scan_y < 8'd72) && (scan_x >= 8'd136) && (scan_x < 8'd160)) begin
            text_hit = 1'b1;
            text_id = TEXT_ARM;
            text_chars = 4'd3;
            text_origin_x = 8'd136;
            text_origin_y = 8'd64;
        end else if ((scan_y >= 8'd82) && (scan_y < 8'd90) && (scan_x >= 8'd112) && (scan_x < 8'd128)) begin
            text_hit = 1'b1;
            text_id = TEXT_PC;
            text_chars = 4'd2;
            text_origin_x = 8'd112;
            text_origin_y = 8'd82;
        end else if ((scan_y >= 8'd96) && (scan_y < 8'd104) && (scan_x >= 8'd88) && (scan_x < 8'd152)) begin
            text_hit = 1'b1;
            text_id = TEXT_PCV;
            text_chars = 4'd8;
            text_origin_x = 8'd88;
            text_origin_y = 8'd96;
        end else if ((scan_y >= 8'd154) && (scan_y < 8'd162) && (scan_x >= 8'd104) && (scan_x < 8'd136)) begin
            text_hit = 1'b1;
            text_id = TEXT_HEAT;
            text_chars = 4'd4;
            text_origin_x = 8'd104;
            text_origin_y = 8'd154;
        end
    end

    always @(posedge clk) begin
        if (rst) begin
            for (i = 0; i < 16; i = i + 1) begin
                buckets[i] <= 4'h0;
            end
            last_bucket <= 4'h0;
            debug_bucket <= 8'h00;
            prev_pixel_index <= 16'd0;
            scan_x <= 8'd0;
            scan_y <= 8'd0;
            current_pc <= 32'h0000_0000;
            s1_text_valid <= 1'b0;
            s1_text_id <= TEXT_TITLE;
            s1_char_index <= 4'd0;
            s1_glyph_x <= 3'd0;
            s1_glyph_y <= 3'd0;
            s1_state_bar <= 1'b0;
            s1_enable_box <= 1'b0;
            s1_arm_box <= 1'b0;
            s1_heatmap_cell <= 1'b0;
            s1_intensity <= 4'h0;
            s1_watchdog_enabled <= 1'b0;
            s1_watchdog_armed <= 1'b0;
            s2_text_pixel <= 1'b0;
            s2_state_bar <= 1'b0;
            s2_enable_box <= 1'b0;
            s2_arm_box <= 1'b0;
            s2_heatmap_cell <= 1'b0;
            s2_intensity <= 4'h0;
            s2_watchdog_enabled <= 1'b0;
            s2_watchdog_armed <= 1'b0;
            pixel_data <= RGB_BLACK;
        end else begin
            if (fetch_valid) begin
                last_bucket <= fetch_bucket;
                current_pc <= fetch_addr;
                debug_bucket <= {4'h0, fetch_bucket};
                if (buckets[fetch_bucket] != 4'hf) begin
                    buckets[fetch_bucket] <= buckets[fetch_bucket] + 4'h1;
                end
            end

            if (pixel_advanced) begin
                prev_pixel_index <= pixel_index;
                if (pixel_index == 16'd0 || pixel_index < prev_pixel_index) begin
                    scan_x <= 8'd0;
                    scan_y <= 8'd0;
                end else if (scan_x == 8'd239) begin
                    scan_x <= 8'd0;
                    if (scan_y == 8'd239) begin
                        scan_y <= 8'd0;
                    end else begin
                        scan_y <= scan_y + 8'd1;
                    end
                end else begin
                    scan_x <= scan_x + 8'd1;
                end
            end

            rel_x = scan_x - text_origin_x;
            rel_y = scan_y - text_origin_y;
            s1_text_id <= text_id;
            s1_char_index <= rel_x[6:3];
            s1_glyph_x <= rel_x[2:0];
            s1_glyph_y <= rel_y[2:0];
            s1_text_valid <= text_hit && (rel_x[6:3] < text_chars) &&
                             (rel_x[2:0] < 3'd5) && (rel_y[2:0] < 3'd7);
            s1_state_bar <= (scan_x >= 8'd76) && (scan_x < 8'd164) &&
                            (scan_y >= 8'd48) && (scan_y < 8'd58);
            s1_enable_box <= (scan_x >= 8'd108) && (scan_x < 8'd124) &&
                             (scan_y >= 8'd64) && (scan_y < 8'd74);
            s1_arm_box <= (scan_x >= 8'd168) && (scan_x < 8'd184) &&
                          (scan_y >= 8'd64) && (scan_y < 8'd74);
            s1_heatmap_cell <= (scan_x >= 8'd96) && (scan_x < 8'd144) &&
                               (scan_y >= 8'd174) && (scan_y < 8'd222) &&
                               ((scan_x < 8'd106) ||
                                ((scan_x >= 8'd108) && (scan_x < 8'd118)) ||
                                ((scan_x >= 8'd120) && (scan_x < 8'd130)) ||
                                ((scan_x >= 8'd132) && (scan_x < 8'd142))) &&
                               ((scan_y < 8'd184) ||
                                ((scan_y >= 8'd186) && (scan_y < 8'd196)) ||
                                ((scan_y >= 8'd198) && (scan_y < 8'd208)) ||
                                ((scan_y >= 8'd210) && (scan_y < 8'd220)));
            s1_intensity <= intensity;
            s1_watchdog_enabled <= watchdog_enabled;
            s1_watchdog_armed <= watchdog_armed;

            selected_char = text_char(s1_text_id, s1_char_index);
            selected_row = glyph_row(selected_char, s1_glyph_y);
            if (s1_text_valid) begin
                case (s1_glyph_x)
                    3'd0: s2_text_pixel <= selected_row[4];
                    3'd1: s2_text_pixel <= selected_row[3];
                    3'd2: s2_text_pixel <= selected_row[2];
                    3'd3: s2_text_pixel <= selected_row[1];
                    3'd4: s2_text_pixel <= selected_row[0];
                    default: s2_text_pixel <= 1'b0;
                endcase
            end else begin
                s2_text_pixel <= 1'b0;
            end
            s2_state_bar <= s1_state_bar;
            s2_enable_box <= s1_enable_box;
            s2_arm_box <= s1_arm_box;
            s2_heatmap_cell <= s1_heatmap_cell;
            s2_intensity <= s1_intensity;
            s2_watchdog_enabled <= s1_watchdog_enabled;
            s2_watchdog_armed <= s1_watchdog_armed;

            if (s2_text_pixel) begin
                pixel_data <= RGB_WHITE;
            end else if (s2_state_bar) begin
                pixel_data <= s2_watchdog_armed ? RGB_GREEN :
                              s2_watchdog_enabled ? RGB_AMBER : RGB_RED;
            end else if (s2_enable_box) begin
                pixel_data <= s2_watchdog_enabled ? RGB_GREEN : RGB_RED;
            end else if (s2_arm_box) begin
                pixel_data <= s2_watchdog_armed ? RGB_GREEN : RGB_RED;
            end else if (s2_heatmap_cell) begin
                pixel_data <= heat_color(s2_intensity);
            end else begin
                pixel_data <= RGB_BLACK;
            end
        end
    end
endmodule
