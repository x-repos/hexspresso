#!/bin/bash
# Run all slab DFT calculations sequentially using eq_run.sh wrapper.
#
# Usage:
#   Phase 1: python gen_inputs.py → generates Calcs 1-3
#     ./eq_run.sh nb2o5_cluster.pwi
#   Phase 2: python gen_inputs.py → generates Calcs 4-7 (reads optimized cluster)
#     ./run.sh
#
# Or run everything if all .pwi files already exist:
#     ./run.sh

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"

CALCS=(
    "nb2o5_cluster"
    "h2"
    "slab_clean"
    "slab_H"
    "slab_Nb2O5"
    "slab_Nb2O5_H"
    "slab_Nb2O5_Fe"
    "slab_Nb2O5_Fe_H"
)

for calc in "${CALCS[@]}"; do
    if [ ! -f "${calc}.pwi" ]; then
        echo "SKIP: ${calc}.pwi not found (run notebook first)"
        continue
    fi
    if [ -f "${calc}.pwo" ]; then
        echo "SKIP: ${calc}.pwo already exists"
        continue
    fi
    "$DIR/eq_run.sh" "${calc}.pwi" "${calc}.pwo"
done

echo ""
echo "All calculations finished. Run ./energy.sh and python adsorption.py"
