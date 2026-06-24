#!/bin/sh

mkdir -p payloads
pwd
for IDX in $(seq 1 6);
do
    cd solve_optimal_$IDX
    ./compile_payload.sh
    cp build/payload.wdog ../payloads/payload_$IDX.wdog
    cd ../
done



