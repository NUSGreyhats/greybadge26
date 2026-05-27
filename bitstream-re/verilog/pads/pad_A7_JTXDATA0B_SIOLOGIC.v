// Backward logic cone for output: MIB_R0C29_PIOT0_JTXDATA0B_SIOLOGIC
module cone(
  output MIB_R0C29_PIOT0_JTXDATA0B_SIOLOGIC,
  input  MIB_R0C67_PIOT0_JPADDIB_PIO,
  input  MIB_R11C72_PICR0_JPADDID_PIO,
  input  MIB_R2C72_PICR0_JDIA,
  input  MIB_R8C72_PICR0_DQS2_JDIA,
  input  MIB_R8C72_PICR0_DQS2_JDIB
);
  wire \$auto$verilog_backend.cc:2355:dump_module$198268;
  wire \R10C10_PLC2_inst.sliceD_inst.ff_0.CE;
  reg \R10C10_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R10C7_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R10C9_PLC2_inst.sliceC_inst.ff_0.Q;
  wire \R2C10_PLC2_inst.sliceB_inst.ff_1.CE;
  wire \R2C10_PLC2_inst.sliceC_inst.genblk9.lut4_1.A;
  wire \R2C19_PLC2_inst.sliceA_inst.ff_1.CE;
  reg \R2C19_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R3C13_PLC2_inst.sliceB_inst.ff_0.Q;
  reg \R3C13_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R3C4_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R3C6_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R3C8_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R4C13_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R4C3_PLC2_inst.sliceB_inst.ff_0.Q;
  reg \R4C4_PLC2_inst.sliceC_inst.ff_1.Q;
  reg \R4C5_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R4C6_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R5C10_PLC2_inst.sliceB_inst.ff_1.Q;
  wire \R5C39_PLC2_inst.sliceC_inst.genblk9.lut4_0.C;
  wire \R6C33_PLC2_inst.sliceA_inst.ff_0.CE;
  reg \R6C33_PLC2_inst.sliceA_inst.ff_0.Q;
  reg \R6C7_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R6C8_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceC_inst.ff_1.Q;
  reg \R6C8_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R6C9_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R7C7_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R9C11_PLC2_inst.sliceC_inst.ff_1.Q;
  wire _0600_;
  wire _1705_;
  wire _1769_;
  wire _1779_;
  wire _1861_;
  wire _1927_;
  wire _1931_;
  wire _2000_;
  wire _2016_;
  wire _2028_;
  wire _2060_;
  wire _2119_;
  wire _2131_;
  wire _2135_;
  wire _2146_;
  wire _2169_;
  wire _2308_;
  wire _2371_;
  wire _2376_;
  wire _2378_;
  wire _2379_;
  wire _2380_;
  wire _2381_;
  wire _2388_;
  wire _2494_;
  wire _2615_;
  wire _3952_;
  wire _4147_;
  wire _4552_;
  wire _4562_;
  wire _4668_;
  wire _5043_;
  wire _5085_;
  wire _5114_;
  wire _5122_;
  wire _5124_;
  wire _5125_;
  wire _5126_;
  wire _5127_;
  wire _5707_;
  wire _5708_;
  wire _6308_;
  wire _7056_;
  wire _7281_;
  wire b0;
  wire bx;

  assign _4147_ = MIB_R8C72_PICR0_DQS2_JDIA & _5708_;

  assign _5085_ = ! MIB_R2C72_PICR0_JDIA;

  assign _5707_ = ~ MIB_R8C72_PICR0_DQS2_JDIB;

  assign _5708_ = ~ _0600_;

  assign _6308_ = ~ \R2C10_PLC2_inst.sliceC_inst.genblk9.lut4_1.A;

  assign _7056_ = MIB_R11C72_PICR0_JPADDID_PIO | _5707_;

  assign _7281_ = MIB_R0C67_PIOT0_JPADDIB_PIO | _6308_;

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _1705_ = \R10C10_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _1705_ = \R10C7_PLC2_inst.sliceB_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R10C10_PLC2_inst.sliceD_inst.ff_1.Q  <= _1705_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _1769_ = \R10C7_PLC2_inst.sliceB_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _1769_ = \R7C7_PLC2_inst.sliceB_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R10C7_PLC2_inst.sliceB_inst.ff_1.Q  <= _1769_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _1779_ = \R10C9_PLC2_inst.sliceC_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _1779_ = \R10C10_PLC2_inst.sliceD_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R10C9_PLC2_inst.sliceC_inst.ff_0.Q  <= _1779_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _1861_ = \R2C19_PLC2_inst.sliceB_inst.ff_1.Q ;
    if (\R2C19_PLC2_inst.sliceA_inst.ff_1.CE ) begin
      _1861_ = \R3C13_PLC2_inst.sliceD_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R2C19_PLC2_inst.sliceB_inst.ff_1.Q  <= _1861_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _1927_ = \R3C13_PLC2_inst.sliceB_inst.ff_0.Q ;
    if (\R2C10_PLC2_inst.sliceB_inst.ff_1.CE ) begin
      _1927_ = \R4C13_PLC2_inst.sliceD_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R3C13_PLC2_inst.sliceB_inst.ff_0.Q  <= _1927_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _1931_ = \R3C13_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (_5043_) begin
      _1931_ = \R3C13_PLC2_inst.sliceB_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R3C13_PLC2_inst.sliceD_inst.ff_1.Q  <= _1931_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2000_ = \R3C4_PLC2_inst.sliceC_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2000_ = \R3C6_PLC2_inst.sliceD_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R3C4_PLC2_inst.sliceC_inst.ff_0.Q  <= _2000_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2016_ = \R3C6_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2016_ = \R3C8_PLC2_inst.sliceD_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R3C6_PLC2_inst.sliceD_inst.ff_1.Q  <= _2016_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2028_ = \R3C8_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2028_ = \R5C10_PLC2_inst.sliceB_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R3C8_PLC2_inst.sliceD_inst.ff_1.Q  <= _2028_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2060_ = \R4C13_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2060_ = \R9C11_PLC2_inst.sliceC_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C13_PLC2_inst.sliceD_inst.ff_1.Q  <= _2060_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2119_ = \R4C3_PLC2_inst.sliceB_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2119_ = \R3C4_PLC2_inst.sliceC_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C3_PLC2_inst.sliceB_inst.ff_0.Q  <= _2119_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2131_ = \R4C4_PLC2_inst.sliceC_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2131_ = \R4C3_PLC2_inst.sliceB_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C4_PLC2_inst.sliceC_inst.ff_1.Q  <= _2131_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2135_ = \R4C5_PLC2_inst.sliceA_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2135_ = \R4C4_PLC2_inst.sliceC_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C5_PLC2_inst.sliceA_inst.ff_1.Q  <= _2135_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2146_ = \R4C6_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2146_ = \R4C5_PLC2_inst.sliceA_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C6_PLC2_inst.sliceD_inst.ff_1.Q  <= _2146_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2169_ = \R5C10_PLC2_inst.sliceB_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2169_ = \R6C9_PLC2_inst.sliceD_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R5C10_PLC2_inst.sliceB_inst.ff_1.Q  <= _2169_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2308_ = \R6C33_PLC2_inst.sliceA_inst.ff_0.Q ;
    if (_5114_) begin
      _2308_ = 1'b0;
    end else begin
      if (\R6C33_PLC2_inst.sliceA_inst.ff_0.CE ) begin
        _2308_ = \R5C39_PLC2_inst.sliceC_inst.genblk9.lut4_0.C ;
      end else begin
      end
    end
  end

  always @(posedge G_HPBX0300) begin
      \R6C33_PLC2_inst.sliceA_inst.ff_0.Q  <= _2308_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2371_ = \R6C7_PLC2_inst.sliceC_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2371_ = \R4C6_PLC2_inst.sliceD_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R6C7_PLC2_inst.sliceC_inst.ff_0.Q  <= _2371_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2376_ = \R6C8_PLC2_inst.sliceA_inst.ff_1.Q ;
    if (_5122_) begin
      _2376_ = 1'b0;
    end else begin
      if (\R6C33_PLC2_inst.sliceA_inst.ff_0.CE ) begin
        _2376_ = \R6C8_PLC2_inst.sliceC_inst.ff_1.Q ;
      end else begin
      end
    end
  end

  always @(posedge G_HPBX0300) begin
      \R6C8_PLC2_inst.sliceA_inst.ff_1.Q  <= _2376_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2378_ = \R6C8_PLC2_inst.sliceC_inst.ff_0.Q ;
    if (_5124_) begin
      _2378_ = 1'b0;
    end else begin
      if (\R6C33_PLC2_inst.sliceA_inst.ff_0.CE ) begin
        _2378_ = \R6C8_PLC2_inst.sliceD_inst.ff_0.Q ;
      end else begin
      end
    end
  end

  always @(posedge G_HPBX0300) begin
      \R6C8_PLC2_inst.sliceC_inst.ff_0.Q  <= _2378_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2379_ = \R6C8_PLC2_inst.sliceC_inst.ff_1.Q ;
    if (_5125_) begin
      _2379_ = 1'b0;
    end else begin
      if (\R6C33_PLC2_inst.sliceA_inst.ff_0.CE ) begin
        _2379_ = \R6C8_PLC2_inst.sliceD_inst.ff_1.Q ;
      end else begin
      end
    end
  end

  always @(posedge G_HPBX0300) begin
      \R6C8_PLC2_inst.sliceC_inst.ff_1.Q  <= _2379_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2380_ = \R6C8_PLC2_inst.sliceD_inst.ff_0.Q ;
    if (_5126_) begin
      _2380_ = 1'b0;
    end else begin
      if (\R6C33_PLC2_inst.sliceA_inst.ff_0.CE ) begin
        _2380_ = \R6C33_PLC2_inst.sliceA_inst.ff_0.Q ;
      end else begin
      end
    end
  end

  always @(posedge G_HPBX0300) begin
      \R6C8_PLC2_inst.sliceD_inst.ff_0.Q  <= _2380_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2381_ = \R6C8_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (_5127_) begin
      _2381_ = 1'b0;
    end else begin
      if (\R6C33_PLC2_inst.sliceA_inst.ff_0.CE ) begin
        _2381_ = \R6C8_PLC2_inst.sliceC_inst.ff_0.Q ;
      end else begin
      end
    end
  end

  always @(posedge G_HPBX0300) begin
      \R6C8_PLC2_inst.sliceD_inst.ff_1.Q  <= _2381_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2388_ = \R6C9_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2388_ = \R6C8_PLC2_inst.sliceA_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R6C9_PLC2_inst.sliceD_inst.ff_1.Q  <= _2388_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2494_ = \R7C7_PLC2_inst.sliceB_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2494_ = \R6C7_PLC2_inst.sliceC_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R7C7_PLC2_inst.sliceB_inst.ff_1.Q  <= _2494_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2615_ = \R9C11_PLC2_inst.sliceC_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2615_ = \R10C9_PLC2_inst.sliceC_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R9C11_PLC2_inst.sliceC_inst.ff_1.Q  <= _2615_;
  end

  assign \R2C19_PLC2_inst.sliceA_inst.ff_1.CE = _3952_;

  assign _0600_ = _7056_;

  assign \R2C10_PLC2_inst.sliceC_inst.genblk9.lut4_1.A = _4147_;

  assign \R10C10_PLC2_inst.sliceD_inst.ff_0.CE = _4552_;

  assign \R2C10_PLC2_inst.sliceB_inst.ff_1.CE = _4562_;

  assign \R5C39_PLC2_inst.sliceC_inst.genblk9.lut4_0.C = _7281_;

  assign \R6C33_PLC2_inst.sliceA_inst.ff_0.CE = _4668_;

  assign MIB_R0C29_PIOT0_JTXDATA0B_SIOLOGIC = \R2C19_PLC2_inst.sliceB_inst.ff_1.Q;

  assign _3952_ = 1'bx;

  assign _5043_ = 1'bx;

  assign _4552_ = 1'bx;

  assign _4562_ = 1'bx;

  assign _4668_ = 1'bx;

  assign _5125_ = _5085_;

  assign _5122_ = _5085_;

  assign _5127_ = _5085_;

  assign _5126_ = _5085_;

  assign _5124_ = _5085_;

  assign _5114_ = _5085_;

endmodule
