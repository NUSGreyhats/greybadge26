// Backward logic cone for output: MIB_R0C42_PIOT0_PADDOA_PIO
module cone(
  output MIB_R0C42_PIOT0_PADDOA_PIO
);
  wire \$auto$verilog_backend.cc:2355:dump_module$198268;
  wire \R2C10_PLC2_inst.sliceA_inst.ff_1.DI;
  reg \R2C10_PLC2_inst.sliceA_inst.ff_1.Q;
  wire \R2C19_PLC2_inst.sliceA_inst.ff_1.CE;
  reg \R2C19_PLC2_inst.sliceA_inst.ff_1.Q;
  wire _1837_;
  wire _1860_;
  wire _3952_;
  wire _5014_;
  wire _5368_;
  wire b1;
  wire bx;

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
    _1860_ = \R2C19_PLC2_inst.sliceA_inst.ff_1.Q ;
    if (\R2C19_PLC2_inst.sliceA_inst.ff_1.CE ) begin
      _1860_ = \R2C10_PLC2_inst.sliceA_inst.ff_1.Q ;
    end else begin
    end
  end

  always @(posedge G_HPBX0300) begin
      \R2C19_PLC2_inst.sliceA_inst.ff_1.Q  <= _1860_;
  end

  assign \R2C10_PLC2_inst.sliceA_inst.ff_1.DI = _5368_;

  assign \R2C19_PLC2_inst.sliceA_inst.ff_1.CE = _3952_;

  assign MIB_R0C42_PIOT0_PADDOA_PIO = \R2C19_PLC2_inst.sliceA_inst.ff_1.Q;

  assign _5014_ = 1'bx;

  assign _5368_ = 1'b1;

  assign _3952_ = 1'bx;

endmodule
