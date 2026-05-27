// Backward logic cone for output: MIB_R0C6_PIOT0_PADDOA_PIO
module cone(
  output MIB_R0C6_PIOT0_PADDOA_PIO,
  input  MIB_R0C67_PIOT0_JPADDIB_PIO,
  input  MIB_R11C72_PICR0_JPADDID_PIO,
  input  MIB_R2C72_PICR0_JDIA,
  input  MIB_R8C72_PICR0_DQS2_JDIA,
  input  MIB_R8C72_PICR0_DQS2_JDIB
);
  wire \$auto$verilog_backend.cc:2355:dump_module$198268;
  wire \R10C10_PLC2_inst.sliceD_inst.ff_0.CE;
  wire \R2C10_PLC2_inst.sliceB_inst.ff_1.CE;
  reg \R2C10_PLC2_inst.sliceB_inst.ff_1.Q;
  wire \R2C10_PLC2_inst.sliceC_inst.genblk9.lut4_1.A;
  wire \R2C19_PLC2_inst.sliceA_inst.ff_1.CE;
  wire \R2C6_PLC2_inst.sliceA_inst.genblk9.lut4_1.Z;
  reg \R2C6_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R2C8_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R3C4_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R3C6_PLC2_inst.sliceC_inst.ff_1.Q;
  reg \R3C8_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R4C11_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R4C16_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R4C3_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R4C5_PLC2_inst.sliceA_inst.ff_0.Q;
  reg \R5C10_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R5C11_PLC2_inst.sliceC_inst.ff_0.Q;
  wire \R5C39_PLC2_inst.sliceC_inst.genblk9.lut4_0.C;
  reg \R5C5_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R5C5_PLC2_inst.sliceD_inst.ff_1.Q;
  wire \R6C33_PLC2_inst.sliceA_inst.ff_0.CE;
  reg \R6C33_PLC2_inst.sliceA_inst.ff_0.Q;
  reg \R6C7_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceC_inst.ff_1.Q;
  reg \R6C8_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R7C8_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R7C8_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R8C9_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R8C9_PLC2_inst.sliceD_inst.ff_1.Q;
  wire _0600_;
  wire _1838_;
  wire _1897_;
  wire _1900_;
  wire _2002_;
  wire _2014_;
  wire _2027_;
  wire _2045_;
  wire _2063_;
  wire _2121_;
  wire _2134_;
  wire _2167_;
  wire _2176_;
  wire _2241_;
  wire _2242_;
  wire _2308_;
  wire _2373_;
  wire _2378_;
  wire _2379_;
  wire _2380_;
  wire _2381_;
  wire _2499_;
  wire _2500_;
  wire _2603_;
  wire _2609_;
  wire _3952_;
  wire _4045_;
  wire _4147_;
  wire _4552_;
  wire _4562_;
  wire _4668_;
  wire _5033_;
  wire _5085_;
  wire _5114_;
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
    _1838_ = \R2C10_PLC2_inst.sliceB_inst.ff_1.Q ;
    if (\R2C10_PLC2_inst.sliceB_inst.ff_1.CE ) begin
      _1838_ = \R4C16_PLC2_inst.sliceD_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R2C10_PLC2_inst.sliceB_inst.ff_1.Q  <= _1838_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _1897_ = \R2C6_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (\R2C6_PLC2_inst.sliceA_inst.genblk9.lut4_1.Z ) begin
      _1897_ = 1'b0;
    end else begin
      if (\R2C19_PLC2_inst.sliceA_inst.ff_1.CE ) begin
        _1897_ = \R2C8_PLC2_inst.sliceD_inst.ff_1.Q ;
      end else begin
      end
    end
  end

  always @(posedge G_HPBX0300) begin
      \R2C6_PLC2_inst.sliceD_inst.ff_1.Q  <= _1897_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _1900_ = \R2C8_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (_5033_) begin
      _1900_ = \R2C10_PLC2_inst.sliceB_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R2C8_PLC2_inst.sliceD_inst.ff_1.Q  <= _1900_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2002_ = \R3C4_PLC2_inst.sliceD_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2002_ = \R3C6_PLC2_inst.sliceC_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R3C4_PLC2_inst.sliceD_inst.ff_0.Q  <= _2002_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2014_ = \R3C6_PLC2_inst.sliceC_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2014_ = \R3C8_PLC2_inst.sliceD_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R3C6_PLC2_inst.sliceC_inst.ff_1.Q  <= _2014_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2027_ = \R3C8_PLC2_inst.sliceD_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2027_ = \R5C10_PLC2_inst.sliceA_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R3C8_PLC2_inst.sliceD_inst.ff_0.Q  <= _2027_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2045_ = \R4C11_PLC2_inst.sliceA_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2045_ = \R5C11_PLC2_inst.sliceC_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C11_PLC2_inst.sliceA_inst.ff_1.Q  <= _2045_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2063_ = \R4C16_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2063_ = \R4C11_PLC2_inst.sliceA_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C16_PLC2_inst.sliceD_inst.ff_1.Q  <= _2063_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2121_ = \R4C3_PLC2_inst.sliceC_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2121_ = \R3C4_PLC2_inst.sliceD_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C3_PLC2_inst.sliceC_inst.ff_0.Q  <= _2121_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2134_ = \R4C5_PLC2_inst.sliceA_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2134_ = \R4C3_PLC2_inst.sliceC_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C5_PLC2_inst.sliceA_inst.ff_0.Q  <= _2134_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2167_ = \R5C10_PLC2_inst.sliceA_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2167_ = \R7C8_PLC2_inst.sliceB_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R5C10_PLC2_inst.sliceA_inst.ff_1.Q  <= _2167_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2176_ = \R5C11_PLC2_inst.sliceC_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2176_ = \R8C9_PLC2_inst.sliceD_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R5C11_PLC2_inst.sliceC_inst.ff_0.Q  <= _2176_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2241_ = \R5C5_PLC2_inst.sliceD_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2241_ = \R4C5_PLC2_inst.sliceA_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R5C5_PLC2_inst.sliceD_inst.ff_0.Q  <= _2241_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2242_ = \R5C5_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2242_ = \R5C5_PLC2_inst.sliceD_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R5C5_PLC2_inst.sliceD_inst.ff_1.Q  <= _2242_;
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
    _2373_ = \R6C7_PLC2_inst.sliceD_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2373_ = \R5C5_PLC2_inst.sliceD_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R6C7_PLC2_inst.sliceD_inst.ff_0.Q  <= _2373_;
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
    _2499_ = \R7C8_PLC2_inst.sliceB_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2499_ = \R6C8_PLC2_inst.sliceC_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R7C8_PLC2_inst.sliceB_inst.ff_1.Q  <= _2499_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2500_ = \R7C8_PLC2_inst.sliceC_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2500_ = \R6C7_PLC2_inst.sliceD_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R7C8_PLC2_inst.sliceC_inst.ff_0.Q  <= _2500_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2603_ = \R8C9_PLC2_inst.sliceA_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2603_ = \R7C8_PLC2_inst.sliceC_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R8C9_PLC2_inst.sliceA_inst.ff_1.Q  <= _2603_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2609_ = \R8C9_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2609_ = \R8C9_PLC2_inst.sliceA_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R8C9_PLC2_inst.sliceD_inst.ff_1.Q  <= _2609_;
  end

  assign \R2C19_PLC2_inst.sliceA_inst.ff_1.CE = _3952_;

  assign \R2C6_PLC2_inst.sliceA_inst.genblk9.lut4_1.Z = _4045_;

  assign _0600_ = _7056_;

  assign \R2C10_PLC2_inst.sliceC_inst.genblk9.lut4_1.A = _4147_;

  assign \R10C10_PLC2_inst.sliceD_inst.ff_0.CE = _4552_;

  assign \R2C10_PLC2_inst.sliceB_inst.ff_1.CE = _4562_;

  assign \R5C39_PLC2_inst.sliceC_inst.genblk9.lut4_0.C = _7281_;

  assign \R6C33_PLC2_inst.sliceA_inst.ff_0.CE = _4668_;

  assign MIB_R0C6_PIOT0_PADDOA_PIO = \R2C6_PLC2_inst.sliceD_inst.ff_1.Q;

  assign _3952_ = 1'bx;

  assign _4045_ = 1'bx;

  assign _5033_ = 1'bx;

  assign _4552_ = 1'bx;

  assign _4562_ = 1'bx;

  assign _4668_ = 1'bx;

  assign _5125_ = _5085_;

  assign _5127_ = _5085_;

  assign _5126_ = _5085_;

  assign _5124_ = _5085_;

  assign _5114_ = _5085_;

endmodule
