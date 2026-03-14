#!/bin/bash
echo "RESULTS SUMMARY"
printf "%-30s %-20s %s\n" "Filename" "Composition" "Final Energy (Ry)"
echo "----------------------------------------------------------------"

for f in *.pwo; do
    if [ -f "$f" ]; then
        # 1. Extract atoms
        TOTAL_ATOMS=$(grep "number of atoms/cell" "$f" | head -1 | awk '{print $NF}')

        # 2. Extract composition (only if atoms were found)
        if [ -n "$TOTAL_ATOMS" ]; then
            COMPOSITION=$(grep -A "$TOTAL_ATOMS" "site n." "$f" | tail -"$TOTAL_ATOMS" | awk '{print $2}' | sort | uniq -c | awk '{printf "%s%s ", $1, $2}')
        else
            COMPOSITION="Pending..."
        fi

        # 3. Extract final energy
        ENERGY=$(grep "!" "$f" | tail -1 | awk '{print $5}')

        # 4. Print logic
        if [ -n "$ENERGY" ]; then
            printf "%-30s %-20s %s Ry\n" "$f" "$COMPOSITION" "$ENERGY"
        else
            # If energy is missing, show the file with a warning
            printf "%-30s %-20s %s\n" "$f" "$COMPOSITION" "--- NOT CONVERGED ---"
        fi
    fi
done
