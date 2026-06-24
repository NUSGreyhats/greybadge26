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

cd empty
./compile_payload.sh
cp build/payload.wdog ../payloads/empty.wdog
cd ../

cd env
./compile_payload.sh
cp build/payload.wdog ../payloads/env.wdog
cd ../

cd solve_naive
./compile_payload.sh
cp build/payload.wdog ../payloads/naive.wdog
cd ../

cd solve_mmio_fuzzing
./compile_payload.sh
cp build/payload.wdog ../payloads/mmio_fuzzing.wdog
cd ../

cd solve_cheat
./compile_payload.sh
cp build/payload.wdog ../payloads/cheat.wdog
cd ../