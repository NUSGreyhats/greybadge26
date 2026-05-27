// Consolidated RTL: union of backward cones of all used output pads.
// Recovered from bitstream main.bit (LFE5U-25F-6CABGA256) by ecpunpack +
// VoidMercy ECP5 decompiler + Yosys synth, condensed and re-parsed.
module pad_behavior(
  output MIB_R0C11_PIOT0_JTXDATA0A_SIOLOGIC,
  output MIB_R0C13_PIOT0_PADDOB_PIO,
  output MIB_R0C15_PIOT0_PADDOA_PIO,
  output MIB_R0C20_PIOT0_JTXDATA0B_SIOLOGIC,
  output MIB_R0C22_PIOT0_JTXDATA0A_SIOLOGIC,
  output MIB_R0C29_PIOT0_JTXDATA0B_SIOLOGIC,
  output MIB_R0C29_PIOT0_PADDTB_PIO,
  output MIB_R0C35_PIOT0_JTSDATA0B_SIOLOGIC,
  output MIB_R0C38_PIOT0_PADDTA_PIO,
  output MIB_R0C42_PIOT0_JTXDATA0B_SIOLOGIC,
  output MIB_R0C42_PIOT0_PADDOA_PIO,
  output MIB_R0C42_PIOT0_PADDTA_PIO,
  output MIB_R0C42_PIOT0_PADDTB_PIO,
  output MIB_R0C44_PIOT0_PADDTA_PIO,
  output MIB_R0C49_PIOT0_JTSDATA0A_SIOLOGIC,
  output MIB_R0C49_PIOT0_PADDOA_PIO,
  output MIB_R0C53_PIOT0_JTSDATA0A_SIOLOGIC,
  output MIB_R0C53_PIOT0_JTXDATA0A_SIOLOGIC,
  output MIB_R0C53_PIOT0_PADDOB_PIO,
  output MIB_R0C53_PIOT0_PADDTB_PIO,
  output MIB_R0C56_PIOT0_JTSDATA0A_SIOLOGIC,
  output MIB_R0C56_PIOT0_PADDOA_PIO,
  output MIB_R0C60_PIOT0_PADDOA_PIO,
  output MIB_R0C60_PIOT0_PADDTA_PIO,
  output MIB_R0C65_PIOT0_JTSDATA0A_SIOLOGIC,
  output MIB_R0C65_PIOT0_JTXDATA0A_SIOLOGIC,
  output MIB_R0C65_PIOT0_JTXDATA0B_SIOLOGIC,
  output MIB_R0C65_PIOT0_PADDTB_PIO,
  output MIB_R0C67_PIOT0_JTSDATA0A_SIOLOGIC,
  output MIB_R0C67_PIOT0_JTXDATA0A_SIOLOGIC,
  output MIB_R0C6_PIOT0_JTSDATA0B_SIOLOGIC,
  output MIB_R0C6_PIOT0_PADDOA_PIO,
  output MIB_R0C6_PIOT0_PADDTA_PIO,
  output MIB_R0C9_PIOT0_JTXDATA0B_SIOLOGIC,
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
  wire \R2C10_PLC2_inst.sliceA_inst.ff_1.DI;
  reg \R2C10_PLC2_inst.sliceA_inst.ff_1.Q;
  wire \R2C10_PLC2_inst.sliceB_inst.ff_1.CE;
  reg \R2C10_PLC2_inst.sliceB_inst.ff_1.Q;
  wire \R2C10_PLC2_inst.sliceC_inst.genblk9.lut4_1.A;
  wire \R2C11_PLC2_inst.sliceA_inst.genblk9.lut4_1.Z;
  wire \R2C11_PLC2_inst.sliceB_inst.genblk9.lut4_1.Z;
  wire \R2C11_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;
  wire \R2C11_PLC2_inst.sliceD_inst.genblk9.lut4_0.Z;
  wire \R2C19_PLC2_inst.sliceA_inst.ff_1.CE;
  reg \R2C19_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R2C19_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R2C19_PLC2_inst.sliceC_inst.ff_0.Q;
  wire \R2C29_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;
  wire \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.D;
  wire \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z;
  wire \R2C53_PLC2_inst.sliceB_inst.genblk9.lut4_1.Z;
  wire \R2C53_PLC2_inst.sliceC_inst.genblk9.lut4_0.Z;
  wire \R2C55_PLC2_inst.sliceB_inst.genblk9.lut4_1.Z;
  wire \R2C60_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z;
  wire \R2C60_PLC2_inst.sliceD_inst.genblk9.lut4_0.Z;
  wire \R2C64_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;
  wire \R2C65_PLC2_inst.sliceB_inst.genblk9.lut4_1.Z;
  wire \R2C6_PLC2_inst.sliceA_inst.genblk9.lut4_1.Z;
  reg \R2C6_PLC2_inst.sliceD_inst.ff_1.Q;
  wire \R2C7_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;
  reg \R2C8_PLC2_inst.sliceD_inst.ff_1.Q;
  wire \R2C9_PLC2_inst.sliceA_inst.genblk9.lutx_mux.Z;
  reg \R3C12_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R3C13_PLC2_inst.sliceB_inst.ff_0.Q;
  reg \R3C13_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R3C4_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R3C4_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R3C6_PLC2_inst.sliceC_inst.ff_1.Q;
  reg \R3C6_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R3C7_PLC2_inst.sliceC_inst.ff_1.Q;
  reg \R3C7_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R3C8_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R3C8_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R4C11_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R4C12_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R4C13_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R4C16_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R4C3_PLC2_inst.sliceB_inst.ff_0.Q;
  reg \R4C3_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R4C4_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R4C4_PLC2_inst.sliceC_inst.ff_1.Q;
  reg \R4C5_PLC2_inst.sliceA_inst.ff_0.Q;
  reg \R4C5_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R4C5_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R4C5_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R4C6_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R4C6_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R4C8_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R4C8_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R4C8_PLC2_inst.sliceC_inst.ff_1.Q;
  reg \R5C10_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R5C10_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R5C11_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R5C12_PLC2_inst.sliceB_inst.ff_1.Q;
  wire \R5C39_PLC2_inst.sliceC_inst.genblk9.lut4_0.C;
  reg \R5C5_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R5C5_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R5C9_PLC2_inst.sliceD_inst.ff_1.Q;
  wire \R6C33_PLC2_inst.sliceA_inst.ff_0.CE;
  reg \R6C33_PLC2_inst.sliceA_inst.ff_0.Q;
  reg \R6C7_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R6C7_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceA_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R6C8_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R6C8_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceC_inst.ff_1.Q;
  reg \R6C8_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R6C8_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R6C9_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R6C9_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R7C10_PLC2_inst.sliceB_inst.ff_0.Q;
  reg \R7C10_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R7C7_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R7C8_PLC2_inst.sliceB_inst.ff_0.Q;
  reg \R7C8_PLC2_inst.sliceB_inst.ff_1.Q;
  reg \R7C8_PLC2_inst.sliceC_inst.ff_0.Q;
  reg \R8C9_PLC2_inst.sliceA_inst.ff_1.Q;
  reg \R8C9_PLC2_inst.sliceD_inst.ff_0.Q;
  reg \R8C9_PLC2_inst.sliceD_inst.ff_1.Q;
  reg \R9C11_PLC2_inst.sliceC_inst.ff_1.Q;
  wire _0447_;
  wire _0600_;
  wire _1705_;
  wire _1769_;
  wire _1779_;
  wire _1837_;
  wire _1838_;
  wire _1860_;
  wire _1861_;
  wire _1862_;
  wire _1897_;
  wire _1900_;
  wire _1919_;
  wire _1927_;
  wire _1931_;
  wire _2000_;
  wire _2002_;
  wire _2014_;
  wire _2016_;
  wire _2021_;
  wire _2022_;
  wire _2027_;
  wire _2028_;
  wire _2045_;
  wire _2055_;
  wire _2060_;
  wire _2063_;
  wire _2119_;
  wire _2121_;
  wire _2130_;
  wire _2131_;
  wire _2134_;
  wire _2135_;
  wire _2138_;
  wire _2139_;
  wire _2145_;
  wire _2146_;
  wire _2155_;
  wire _2156_;
  wire _2157_;
  wire _2167_;
  wire _2169_;
  wire _2176_;
  wire _2182_;
  wire _2241_;
  wire _2242_;
  wire _2270_;
  wire _2308_;
  wire _2371_;
  wire _2373_;
  wire _2375_;
  wire _2376_;
  wire _2377_;
  wire _2378_;
  wire _2379_;
  wire _2380_;
  wire _2381_;
  wire _2382_;
  wire _2388_;
  wire _2391_;
  wire _2392_;
  wire _2494_;
  wire _2498_;
  wire _2499_;
  wire _2500_;
  wire _2603_;
  wire _2608_;
  wire _2609_;
  wire _2615_;
  wire _3893_;
  wire _3898_;
  wire _3952_;
  wire _4018_;
  wire _4025_;
  wire _4045_;
  wire _4147_;
  wire _4552_;
  wire _4562_;
  wire _4668_;
  wire _5014_;
  wire _5033_;
  wire _5038_;
  wire _5043_;
  wire _5085_;
  wire _5114_;
  wire _5121_;
  wire _5122_;
  wire _5123_;
  wire _5124_;
  wire _5125_;
  wire _5126_;
  wire _5127_;
  wire _5368_;
  wire _5482_;
  wire _5510_;
  wire _5545_;
  wire _5707_;
  wire _5708_;
  wire _6308_;
  wire _6974_;
  wire _6975_;
  wire _6981_;
  wire _6989_;
  wire _6990_;
  wire _6993_;
  wire _6995_;
  wire _7056_;
  wire _7281_;
  wire _7735_;
  wire _7736_;
  wire _7819_;
  wire _7825_;
  wire b0;
  wire b1;
  wire bx;

  assign _4025_ = MIB_R8C72_PICR0_DQS2_JDIB & _5545_;

  assign _4147_ = MIB_R8C72_PICR0_DQS2_JDIA & _5708_;

  assign _5085_ = ! MIB_R2C72_PICR0_JDIA;

  assign _5510_ = ~ \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.D;

  assign _5545_ = ~ _0447_;

  assign _5707_ = ~ MIB_R8C72_PICR0_DQS2_JDIB;

  assign _5708_ = ~ _0600_;

  assign _6308_ = ~ \R2C10_PLC2_inst.sliceC_inst.genblk9.lut4_1.A;

  assign _6981_ = MIB_R11C72_PICR0_JPADDID_PIO | MIB_R8C72_PICR0_DQS2_JDIA;

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
    _1837_ = \R2C10_PLC2_inst.sliceA_inst.ff_1.Q ;
    if (_5014_) begin
      _1837_ = \R2C10_PLC2_inst.sliceA_inst.ff_1.DI ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R2C10_PLC2_inst.sliceA_inst.ff_1.Q  <= _1837_;
  end

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
    _1860_ = \R2C19_PLC2_inst.sliceA_inst.ff_1.Q ;
    if (\R2C19_PLC2_inst.sliceA_inst.ff_1.CE ) begin
      _1860_ = \R2C10_PLC2_inst.sliceA_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R2C19_PLC2_inst.sliceA_inst.ff_1.Q  <= _1860_;
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
    _2608_ = \R8C9_PLC2_inst.sliceD_inst.ff_0.Q ;
    if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE ) begin
      _2608_ = \R7C8_PLC2_inst.sliceB_inst.ff_0.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R8C9_PLC2_inst.sliceD_inst.ff_0.Q  <= _2608_;
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

  assign \R2C10_PLC2_inst.sliceA_inst.ff_1.DI = _5368_;

  assign \R2C11_PLC2_inst.sliceA_inst.genblk9.lut4_1.Z = _3893_;

  assign \R2C11_PLC2_inst.sliceB_inst.genblk9.lut4_1.Z = _7735_;

  assign \R2C11_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z = _7736_;

  assign \R2C11_PLC2_inst.sliceD_inst.genblk9.lut4_0.Z = _3898_;

  assign \R2C19_PLC2_inst.sliceA_inst.ff_1.CE = _3952_;

  assign \R2C29_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z = _5482_;

  assign \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z = _5510_;

  assign \R2C53_PLC2_inst.sliceB_inst.genblk9.lut4_1.Z = _6974_;

  assign \R2C53_PLC2_inst.sliceC_inst.genblk9.lut4_0.Z = _6975_;

  assign \R2C55_PLC2_inst.sliceB_inst.genblk9.lut4_1.Z = _4018_;

  assign _0447_ = _6981_;

  assign \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.D = _4025_;

  assign \R2C60_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z = _6989_;

  assign \R2C60_PLC2_inst.sliceD_inst.genblk9.lut4_0.Z = _6990_;

  assign \R2C64_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z = _6993_;

  assign \R2C65_PLC2_inst.sliceB_inst.genblk9.lut4_1.Z = _6995_;

  assign \R2C6_PLC2_inst.sliceA_inst.genblk9.lut4_1.Z = _4045_;

  assign \R2C7_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z = _7819_;

  assign \R2C9_PLC2_inst.sliceA_inst.genblk9.lutx_mux.Z = _7825_;

  assign _0600_ = _7056_;

  assign \R2C10_PLC2_inst.sliceC_inst.genblk9.lut4_1.A = _4147_;

  assign \R10C10_PLC2_inst.sliceD_inst.ff_0.CE = _4552_;

  assign \R2C10_PLC2_inst.sliceB_inst.ff_1.CE = _4562_;

  assign \R5C39_PLC2_inst.sliceC_inst.genblk9.lut4_0.C = _7281_;

  assign \R6C33_PLC2_inst.sliceA_inst.ff_0.CE = _4668_;

  assign MIB_R0C11_PIOT0_JTXDATA0A_SIOLOGIC = \R2C9_PLC2_inst.sliceA_inst.genblk9.lutx_mux.Z;

  assign MIB_R0C13_PIOT0_PADDOB_PIO = \R2C11_PLC2_inst.sliceA_inst.genblk9.lut4_1.Z;

  assign MIB_R0C15_PIOT0_PADDOA_PIO = \R2C11_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;

  assign MIB_R0C20_PIOT0_JTXDATA0B_SIOLOGIC = \R2C11_PLC2_inst.sliceD_inst.genblk9.lut4_0.Z;

  assign MIB_R0C22_PIOT0_JTXDATA0A_SIOLOGIC = \R2C11_PLC2_inst.sliceB_inst.genblk9.lut4_1.Z;

  assign MIB_R0C29_PIOT0_JTXDATA0B_SIOLOGIC = \R2C19_PLC2_inst.sliceB_inst.ff_1.Q;

  assign MIB_R0C29_PIOT0_PADDTB_PIO = \R2C29_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;

  assign MIB_R0C35_PIOT0_JTSDATA0B_SIOLOGIC = \R2C29_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;

  assign MIB_R0C38_PIOT0_PADDTA_PIO = \R2C29_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;

  assign MIB_R0C42_PIOT0_JTXDATA0B_SIOLOGIC = \R2C19_PLC2_inst.sliceC_inst.ff_0.Q;

  assign MIB_R0C42_PIOT0_PADDOA_PIO = \R2C19_PLC2_inst.sliceA_inst.ff_1.Q;

  assign MIB_R0C42_PIOT0_PADDTA_PIO = \R2C29_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;

  assign MIB_R0C42_PIOT0_PADDTB_PIO = \R2C29_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;

  assign MIB_R0C44_PIOT0_PADDTA_PIO = \R2C29_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;

  assign MIB_R0C49_PIOT0_JTSDATA0A_SIOLOGIC = \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z;

  assign MIB_R0C49_PIOT0_PADDOA_PIO = 1'b0;

  assign MIB_R0C53_PIOT0_JTSDATA0A_SIOLOGIC = \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z;

  assign MIB_R0C53_PIOT0_JTXDATA0A_SIOLOGIC = \R2C53_PLC2_inst.sliceC_inst.genblk9.lut4_0.Z;

  assign MIB_R0C53_PIOT0_PADDOB_PIO = \R2C53_PLC2_inst.sliceB_inst.genblk9.lut4_1.Z;

  assign MIB_R0C53_PIOT0_PADDTB_PIO = \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z;

  assign MIB_R0C56_PIOT0_JTSDATA0A_SIOLOGIC = \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z;

  assign MIB_R0C56_PIOT0_PADDOA_PIO = \R2C55_PLC2_inst.sliceB_inst.genblk9.lut4_1.Z;

  assign MIB_R0C60_PIOT0_PADDOA_PIO = \R2C60_PLC2_inst.sliceD_inst.genblk9.lut4_0.Z;

  assign MIB_R0C60_PIOT0_PADDTA_PIO = \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z;

  assign MIB_R0C65_PIOT0_JTSDATA0A_SIOLOGIC = \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z;

  assign MIB_R0C65_PIOT0_JTXDATA0A_SIOLOGIC = \R2C60_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z;

  assign MIB_R0C65_PIOT0_JTXDATA0B_SIOLOGIC = \R2C64_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;

  assign MIB_R0C65_PIOT0_PADDTB_PIO = \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z;

  assign MIB_R0C67_PIOT0_JTSDATA0A_SIOLOGIC = \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z;

  assign MIB_R0C67_PIOT0_JTXDATA0A_SIOLOGIC = \R2C65_PLC2_inst.sliceB_inst.genblk9.lut4_1.Z;

  assign MIB_R0C6_PIOT0_JTSDATA0B_SIOLOGIC = \R2C29_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;

  assign MIB_R0C6_PIOT0_PADDOA_PIO = \R2C6_PLC2_inst.sliceD_inst.ff_1.Q;

  assign MIB_R0C6_PIOT0_PADDTA_PIO = \R2C29_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;

  assign MIB_R0C9_PIOT0_JTXDATA0B_SIOLOGIC = \R2C7_PLC2_inst.sliceC_inst.genblk9.lut4_1.Z;

  assign _5014_ = 1'bx;

  assign _5368_ = 1'b1;

  assign _3893_ = 1'bx;

  assign _7735_ = 1'bx;

  assign _7736_ = 1'bx;

  assign _3898_ = 1'bx;

  assign _3952_ = 1'bx;

  assign _5482_ = 1'b1;

  assign _6974_ = 1'b1;

  assign _6975_ = 1'b1;

  assign _4018_ = 1'b0;

  assign _6989_ = 1'b1;

  assign _6990_ = 1'b1;

  assign _6993_ = 1'b1;

  assign _6995_ = 1'b1;

  assign _4045_ = 1'bx;

  assign _7819_ = 1'bx;

  assign _5033_ = 1'bx;

  assign _7825_ = 1'bx;

  assign _5038_ = 1'bx;

  assign _5043_ = 1'bx;

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
