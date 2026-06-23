PROJ=main

all: log ${PROJ}.bit

log:
	mkdir -p log

tmp.v: 
	find src -name '*.v' -print | sort | xargs cat > tmp.v

%.json: tmp.v
	yosys -p "synth_ecp5 -top top -json $@" $< | tee log/yosys.log

%_out.config: %.json
	nextpnr-ecp5 --json $< --textcfg $@ --25k --package CABGA256 --lpf pinout.lpf  | tee log/nextpnr-ecp5.log

%.bit: %_out.config
	ecppack --svf ${PROJ}.svf $< $@ | tee log/ecppack.log

${PROJ}.svf : ${PROJ}.bit

clean:
	rm -f *.svf *.bit *.config *.json tmp.v 

.PHONY: all prog clean log
