# Slab DFT: H2 Adsorption on Mg2Ni(0001) with Nb2O5/Fe Catalysts

## Goal

Compare how Nb2O5 and Fe nanoparticle catalysts affect hydrogen adsorption at the Mg2Ni surface using slab + vacuum DFT models.

**Three systems:**
1. Mg2Ni(0001) + H (baseline)
2. Mg2Ni(0001) + Nb2O5 + H (catalyst effect)
3. Mg2Ni(0001) + Nb2O5 + Fe + H (co-catalyst effect)

**Metric:** H2 adsorption energy:
```
E_ads = E(slab+H) - E(slab) - (n/2)·E(H2_gas)
```

## Calculations

| Calc | System | Atoms | File |
|------|--------|-------|------|
| 0 | Nb2O5 cluster (isolated optimization) | 7 | `nb2o5_cluster.pwi` |
| 1 | H2 gas reference | 2 | `h2.pwi` |
| 2 | Clean Mg2Ni(0001) slab | 144 | `slab_clean.pwi` |
| 3 | Slab + H | 145 | `slab_H.pwi` |
| 4 | Slab + Nb2O5 | 151 | `slab_Nb2O5.pwi` |
| 5 | Slab + Nb2O5 + H | 152 | `slab_Nb2O5_H.pwi` |
| 6 | Slab + Nb2O5 + Fe | 152 | `slab_Nb2O5_Fe.pwi` |
| 7 | Slab + Nb2O5 + Fe + H | 153 | `slab_Nb2O5_Fe_H.pwi` |

## Slab Construction

- **Bulk source:** `../mgh2-cif/cif/mg2ni-P62.cif` (Mg2Ni, P6222, a=b=5.197 Å, c=13.202 Å)
- **Supercell:** 2×2×2 (144 atoms: 96 Mg + 48 Ni)
- **Vacuum:** 12 Å per side (24 Å total)
- **Constraints:** Bottom half of slab atoms fixed (FixAtoms)
- **K-points:** 4×4×1 (slab), gamma-point (H2, Nb2O5 cluster)

## DFT Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `calculation` | `relax` | Not vc-relax — cell fixed with vacuum |
| `ecutwfc` | 60 Ry | |
| `ecutrho` | 480 Ry | Reduced from 800 to fit in 32 GB VRAM |
| `conv_thr` | 1.2e-9 | |
| `mixing_beta` | 0.2 | |
| `electron_maxstep` | 200 | |
| `nspin` | 2 | Ni, Fe, Nb are magnetic |
| `dipfield/tefield` | True | Dipole correction for asymmetric slab |
| `edir` | 3 | Correction along z-axis |
| `emaxpos` | 0.95 | Sawtooth position (in vacuum) |
| `eopreg` | 0.05 | Sawtooth width |

## Nb2O5 Cluster

Edge-sharing NbO6 dimer fragment (2 Nb + 5 O):
- Optimized in isolation first (Calc 0, ecutrho=800, gamma-point)
- Placed on slab centered laterally, 2.2 Å above top surface
- Bottom bridging O faces the slab

## Pseudopotentials

| Element | File |
|---------|------|
| Mg | `Mg.pbe-n-kjpaw_psl.0.3.0.UPF` |
| Ni | `ni_pbe_v1.4.uspp.F.UPF` |
| H | `H.pbe-rrkjus_psl.1.0.0.UPF` |
| Nb | `Nb.pbe-spn-kjpaw_psl.0.3.0.UPF` |
| O | `O.pbe-n-kjpaw_psl.0.1.UPF` |
| Fe | `Fe.pbe-spn-kjpaw_psl.0.2.1.UPF` |

## Workflow

```
1. Generate Calcs 1-3 inputs       python gen_inputs.py  (Phase 1)
2. Run Calc 0: Nb2O5 cluster       ./eq_run.sh nb2o5_cluster.pwi
3. Generate Calcs 4-7 inputs       python gen_inputs.py  (Phase 2, reads optimized cluster)
4. Run all remaining calculations   ./run.sh  (skips completed calcs)
5. Extract energies                 ./energy.sh
6. Compute adsorption energies      python adsorption.py
```

## File Layout

```
mgh2-slab/
├── gen_inputs.py             # Structure generation script (ASE → .pwi)
├── eq_run.sh                 # pw.x wrapper (handles LD_PRELOAD for GPU build)
├── run.sh                    # Run all calculations sequentially
├── energy.sh                 # Extract energies from .pwo files
├── adsorption.py             # Compute adsorption energies
├── out/                      # QE output directory
├── nb2o5_cluster.pwi/.pwo    # Calc 0: Nb2O5 cluster (DONE)
├── h2.pwi/.pwo               # Calc 1: H2 gas
├── slab_clean.pwi/.pwo       # Calc 2: Clean slab
├── slab_H.pwi/.pwo           # Calc 3: Slab + H
├── slab_Nb2O5.pwi/.pwo       # Calc 4: Slab + Nb2O5
├── slab_Nb2O5_H.pwi/.pwo     # Calc 5: Slab + Nb2O5 + H
├── slab_Nb2O5_Fe.pwi/.pwo    # Calc 6: Slab + Nb2O5 + Fe
└── slab_Nb2O5_Fe_H.pwi/.pwo  # Calc 7: Slab + Nb2O5 + Fe + H
```

## Hardware Notes

- GPU: 32 GB VRAM, System: 60 GB RAM
- Estimated memory per slab calc: ~143 GB at ecutrho=800 (split across GPU + CPU)
- Reduced ecutrho to 480 to fit hardware (2×2×2 supercell = 144 atoms)

## Expected Results

- H2 gas energy: ~-2.333 Ry (consistent with previous bulk calculations)
- E_ads for H on clean Mg2Ni: -0.5 to -2.0 eV (typical H chemisorption)
- Catalyst effect: Nb2O5 and Fe should modify E_ads compared to baseline
- Conversion: 1 Ry = 13.6057 eV = 1312.75 kJ/mol
