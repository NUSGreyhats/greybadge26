// Backward logic cone for output: MIB_R0C42_PIOT0_JTXDATA0B_SIOLOGIC
module cone(
  output MIB_R0C42_PIOT0_JTXDATA0B_SIOLOGIC,
  input  MIB_R0C67_PIOT0_JPADDIB_PIO,
  input  MIB_R11C72_PICR0_JPADDID_PIO,
  input  MIB_R2C72_PICR0_JDIA,
  input  MIB_R8C72_PICR0_DQS2_JDIA,
  input  MIB_R8C72_PICR0_DQS2_JDIB
);
  wire \$auto$verilog_backend.cc:2355:dump_module$198268;
  wire \R10C10_PLC2_inst.sliceD_inst.ff_0.CE;
  wire \R2C10_PLC2_inst.sliceB_inst.ff_1.CE;
  wire \R2C10_PLC2_inst.sliceC_inst.genblk9.lut4_1.A;
  wire \R2C19_PLC2_inst.sliceA_inst.ff_1.CE;
  reg \R2C19_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R3C12_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R3C7_PLC2_inst.sliceC_inst.ff_1.Q;
  reg \R3C7_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R4C12_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R4C4_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R4C5_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R4C5_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R4C6_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R4C8_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R4C8_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R4C8_PLC2_inst.sliceC_inst.ff_1.Q;
  reg \R5C12_PLC2_inst.sliceB_inst.ff_1.Q;
  wire \R5C39_PLC2_inst.sliceC_inst.genblk9.lut4_0.C;
  reg \R5C9_PLC2_inst.sliceD_inst.ff_1.Q;
  wire \R6C33_PLC2_inst.sliceA_inst.ff_0.CE;
  reg \R6C33_PLC2_inst.sliceA_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceA_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R6C8_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R6C8_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceC_inst.ff_1.Q;
  reg \R6C8_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R6C9_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R7C10_PLC2_inst.sliceB_inst.ff_0.Q;
  reg \R7C10_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R7C8_PLC2_inst.sliceB_inst.ff_0.Q;
  reg \R8C9_PLC2_inst.sliceD_inst.ff_0.Q;
  wire _0600_;
  wire _1862_;
  wire _1919_;
  wire _2021_;
  wire _2022_;
  wire _2055_;
  wire _2130_;
  wire _2138_;
  wire _2139_;
  wire _2145_;
  wire _2155_;
  wire _2156_;
  wire _2157_;
  wire _2182_;
  wire _2270_;
  wire _2308_;
  wire _2375_;
  wire _2376_;
  wire _2377_;
  wire _2378_;
  wire _2379_;
  wire _2380_;
  wire _2381_;
  wire _2382_;
  wire _2391_;
  wire _2392_;
  wire _2498_;
  wire _2608_;
  wire _3952_;
  wire _4147_;
  wire _4552_;
  wire _4562_;
  wire _4668_;
  wire _5038_;
  wire _5085_;
  wire _5114_;
  wire _5121_;
  wire _5122_;
  wire _5123_;
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
    _1862_ = \R2C19_PLC2_inst.sliceC_inst.ff_0.Q ;
    if (\R2C19_PLC2_inst.sliceA_inst.ff_1.CE ) begin
      _1862_ = \R3C12_PLC2_inst.sliceA_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R2C19_PLC2_inst.sliceC_inst.ff_0.Q  <= _1862_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _1919_ = \R3C12_PLC2_inst.sliceA_inst.ff_1.Q ;
    if (_5038_) begin
      _1919_ = \R4C12_PLC2_inst.sliceD_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R3C12_PLC2_inst.sliceA_inst.ff_1.Q  <= _1919_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2021_ = \R3C7_PLC2_inst.sliceC_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2021_ = \R5C9_PLC2_inst.sliceD_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R3C7_PLC2_inst.sliceC_inst.ff_1.Q  <= _2021_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2022_ = \R3C7_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2022_ = \R3C7_PLC2_inst.sliceC_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R3C7_PLC2_inst.sliceD_inst.ff_1.Q  <= _2022_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2055_ = \R4C12_PLC2_inst.sliceD_inst.ff_0.Q ;
    if (\R2C10_PLC2_inst.sliceB_inst.ff_1.CE ) begin
      _2055_ = \R5C12_PLC2_inst.sliceB_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C12_PLC2_inst.sliceD_inst.ff_0.Q  <= _2055_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2130_ = \R4C4_PLC2_inst.sliceC_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2130_ = \R4C5_PLC2_inst.sliceD_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C4_PLC2_inst.sliceC_inst.ff_0.Q  <= _2130_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2138_ = \R4C5_PLC2_inst.sliceD_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2138_ = \R3C7_PLC2_inst.sliceD_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C5_PLC2_inst.sliceD_inst.ff_0.Q  <= _2138_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2139_ = \R4C5_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2139_ = \R4C5_PLC2_inst.sliceD_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C5_PLC2_inst.sliceD_inst.ff_1.Q  <= _2139_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2145_ = \R4C6_PLC2_inst.sliceD_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2145_ = \R4C4_PLC2_inst.sliceC_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C6_PLC2_inst.sliceD_inst.ff_0.Q  <= _2145_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2155_ = \R4C8_PLC2_inst.sliceB_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2155_ = \R4C6_PLC2_inst.sliceD_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C8_PLC2_inst.sliceB_inst.ff_1.Q  <= _2155_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2156_ = \R4C8_PLC2_inst.sliceC_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2156_ = \R4C8_PLC2_inst.sliceB_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C8_PLC2_inst.sliceC_inst.ff_0.Q  <= _2156_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2157_ = \R4C8_PLC2_inst.sliceC_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2157_ = \R4C8_PLC2_inst.sliceC_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R4C8_PLC2_inst.sliceC_inst.ff_1.Q  <= _2157_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2182_ = \R5C12_PLC2_inst.sliceB_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2182_ = \R7C10_PLC2_inst.sliceB_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R5C12_PLC2_inst.sliceB_inst.ff_1.Q  <= _2182_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2270_ = \R5C9_PLC2_inst.sliceD_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2270_ = \R6C9_PLC2_inst.sliceA_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R5C9_PLC2_inst.sliceD_inst.ff_1.Q  <= _2270_;
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
    _2375_ = \R6C8_PLC2_inst.sliceA_inst.ff_0.Q ;
    if (_5121_) begin
      _2375_ = 1'b0;
    end else begin
      if (\R6C33_PLC2_inst.sliceA_inst.ff_0.CE ) begin
        _2375_ = \R6C8_PLC2_inst.sliceB_inst.ff_1.Q ;
      end else begin
      end
    end
  end

  always @(posedge G_HPBX0300) begin
      \R6C8_PLC2_inst.sliceA_inst.ff_0.Q  <= _2375_;
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
    _2377_ = \R6C8_PLC2_inst.sliceB_inst.ff_1.Q ;
    if (_5123_) begin
      _2377_ = 1'b0;
    end else begin
      if (\R6C33_PLC2_inst.sliceA_inst.ff_0.CE ) begin
        _2377_ = \R6C8_PLC2_inst.sliceA_inst.ff_1.Q ;
      end else begin
      end
    end
  end

  always @(posedge G_HPBX0300) begin
      \R6C8_PLC2_inst.sliceB_inst.ff_1.Q  <= _2377_;
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
    _2382_ = \R6C9_PLC2_inst.sliceA_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2382_ = \R6C8_PLC2_inst.sliceA_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R6C9_PLC2_inst.sliceA_inst.ff_1.Q  <= _2382_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2391_ = \R7C10_PLC2_inst.sliceB_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2391_ = \R8C9_PLC2_inst.sliceD_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R7C10_PLC2_inst.sliceB_inst.ff_0.Q  <= _2391_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2392_ = \R7C10_PLC2_inst.sliceB_inst.ff_1.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2392_ = \R7C10_PLC2_inst.sliceB_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R7C10_PLC2_inst.sliceB_inst.ff_1.Q  <= _2392_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2498_ = \R7C8_PLC2_inst.sliceB_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2498_ = \R4C8_PLC2_inst.sliceC_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R7C8_PLC2_inst.sliceB_inst.ff_0.Q  <= _2498_;
  end

  always @* begin
    if (\$auto$verilog_backend.cc:2355:dump_module$198268 ) begin end
    _2608_ = \R8C9_PLC2_inst.sliceD_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2608_ = \R7C8_PLC2_inst.sliceB_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R8C9_PLC2_inst.sliceD_inst.ff_0.Q  <= _2608_;
  end

  assign \R2C19_PLC2_inst.sliceA_inst.ff_1.CE = _3952_;

  assign _0600_ = _7056_;

  assign \R2C10_PLC2_inst.sliceC_inst.genblk9.lut4_1.A = _4147_;

  assign \R10C10_PLC2_inst.sliceD_inst.ff_0.CE = _4552_;

  assign \R2C10_PLC2_inst.sliceB_inst.ff_1.CE = _4562_;

  assign \R5C39_PLC2_inst.sliceC_inst.genblk9.lut4_0.C = _7281_;

  assign \R6C33_PLC2_inst.sliceA_inst.ff_0.CE = _4668_;

  assign MIB_R0C42_PIOT0_JTXDATA0B_SIOLOGIC = \R2C19_PLC2_inst.sliceC_inst.ff_0.Q;

  assign _3952_ = 1'bx;

  assign _5038_ = 1'bx;

  assign _4552_ = 1'bx;

  assign _4562_ = 1'bx;

  assign _4668_ = 1'bx;

  assign _5125_ = _5085_;

  assign _5122_ = _5085_;

  assign _5123_ = _5085_;

  assign _5127_ = _5085_;

  assign _5126_ = _5085_;

  assign _5121_ = _5085_;

  assign _5124_ = _5085_;

  assign _5114_ = _5085_;

endmodule
