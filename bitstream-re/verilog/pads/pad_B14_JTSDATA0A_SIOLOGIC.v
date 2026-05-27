// Backward logic cone for output: MIB_R0C67_PIOT0_JTSDATA0A_SIOLOGIC
module cone(
  output MIB_R0C67_PIOT0_JTSDATA0A_SIOLOGIC,
  input  MIB_R11C72_PICR0_JPADDID_PIO,
  input  MIB_R8C72_PICR0_DQS2_JDIA,
  input  MIB_R8C72_PICR0_DQS2_JDIB
);
  wire \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.D;
  wire \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z;
  wire _0447_;
  wire _4025_;
  wire _5510_;
  wire _5545_;
  wire _6981_;

  assign _4025_ = MIB_R8C72_PICR0_DQS2_JDIB & _5545_;

  assign _5510_ = ~ \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.D;

  assign _5545_ = ~ _0447_;

  assign _6981_ = MIB_R11C72_PICR0_JPADDID_PIO | MIB_R8C72_PICR0_DQS2_JDIA;

  assign \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z = _5510_;

  assign _0447_ = _6981_;

  assign \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.D = _4025_;

  assign MIB_R0C67_PIOT0_JTSDATA0A_SIOLOGIC = \R2C49_PLC2_inst.sliceB_inst.genblk9.lut4_0.Z;

endmodule
