PROJ=pio_fpga_comms
LPF=pinout.lpf

all: log ${PROJ}.bit

log:
	mkdir -p log

${PROJ}.json: src/top.v
	yosys -p "synth_ecp5 -top top -json $@" $< | tee log/yosys.log

${PROJ}_out.config: ${PROJ}.json
	nextpnr-ecp5 --json $< --textcfg $@ --25k --package CABGA256 --lpf ${LPF} | tee log/nextpnr-ecp5.log

${PROJ}.bit: ${PROJ}_out.config
	ecppack --svf ${PROJ}.svf $< $@ | tee log/ecppack.log
	mkdir -p ../payloads
	cp $@ ../payloads/$@

${PROJ}.svf: ${PROJ}.bit

clean:
	rm -f *.svf *.bit *.config *.json
	rm -rf log
	rm -f ../payloads/${PROJ}.bit

.PHONY: all clean log
