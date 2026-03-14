#!/bin/bash
# Wrapper to run pw.x with correct environment.
# Avoids shell profile conflicts with NVIDIA OpenMP / HPC-X.
#
# Usage: ./eq_run.sh input.pwi output.pwo

NVHPC=/opt/nvidia/hpc_sdk
CUDA_HOME=$NVHPC/Linux_x86_64/25.9/cuda/13.0
OMPI=$NVHPC/Linux_x86_64/25.9/comm_libs/13.0/hpcx/hpcx-2.24/ompi
COMPILERS=$NVHPC/Linux_x86_64/25.9/compilers
HPCX=$NVHPC/Linux_x86_64/25.9/comm_libs/13.0/hpcx/latest

export LD_LIBRARY_PATH=$OMPI/lib:$COMPILERS/lib:$HPCX/ucx/lib:$HPCX/ucc/lib:$CUDA_HOME/lib64
export LD_PRELOAD=$COMPILERS/lib/libnvomp.so
export NVCOMPILER_OMP_DISABLE_WARNINGS=true
export OMP_NUM_THREADS=16
export CUDA_VISIBLE_DEVICES=0

PW=/home/x/Programs/espresso_gpu/bin/pw.x

INPUT="${1:-}"
OUTPUT="${2:-}"

if [ -z "$INPUT" ]; then
    echo "Usage: $0 input.pwi [output.pwo]"
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    OUTPUT="${INPUT%.pwi}.pwo"
fi

echo "Running: $INPUT -> $OUTPUT"
$PW -in "$INPUT" > "$OUTPUT" 2>&1
echo "Done: $OUTPUT"
