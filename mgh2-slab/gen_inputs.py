"""Generate all QE input files for slab DFT calculations.

Usage: python gen_inputs.py

Requires nb2o5_cluster.pwo to exist (run Calc 0 first for Phase 2 inputs).
"""
from ase.io import read, write
from ase import Atoms
from ase.constraints import FixAtoms
import numpy as np  # noqa: F401 — used by ASE internally

pseudo_dir = '/home/x/Workspace/espresso/pseudo'
all_pseudopotentials = {
    'Mg': 'Mg.pbe-n-kjpaw_psl.0.3.0.UPF',
    'Ni': 'ni_pbe_v1.4.uspp.F.UPF',
    'H':  'H.pbe-rrkjus_psl.1.0.0.UPF',
    'Nb': 'Nb.pbe-spn-kjpaw_psl.0.3.0.UPF',
    'O':  'O.pbe-n-kjpaw_psl.0.1.UPF',
    'Fe': 'Fe.pbe-spn-kjpaw_psl.0.2.1.UPF',
}

# --- Tunable parameters ---
ECUTRHO = 480          # charge density cutoff (Ry)
SUPERCELL = (2, 2, 2)  # slab supercell (2,2,2)=144 atoms, (2,2,1)=72 atoms
SLAB_VACUUM = 12       # vacuum per side (Angstrom)
KPTS = (4, 4, 1)       # k-point mesh for slab calcs

MAGNETIC_MOMENTS = {'Ni': 0.5, 'Fe': 0.5, 'Nb': 0.5}


def set_magnetic_moments(atoms):
    moments = [MAGNETIC_MOMENTS.get(sym, 0.0) for sym in atoms.get_chemical_symbols()]
    atoms.set_initial_magnetic_moments(moments)


def make_slab_input_params(prefix, species_list):
    input_params = {
        'control': {
            'calculation': 'relax',
            'prefix': prefix,
            'outdir': './out/',
            'pseudo_dir': pseudo_dir,
            'tprnfor': True,
            'tstress': False,
            'etot_conv_thr': 1.4e-4,
            'forc_conv_thr': 1.0e-4,
            'max_seconds': 86000,
            'restart_mode': 'from_scratch',
            'dipfield': True,
            'tefield': True,
        },
        'system': {
            'ecutwfc': 60.0,
            'ecutrho': ECUTRHO,
            'occupations': 'smearing',
            'smearing': 'cold',
            'degauss': 0.01,
            'nspin': 2,
            'edir': 3,
            'emaxpos': 0.95,
            'eopreg': 0.05,
        },
        'electrons': {
            'conv_thr': 1.2e-9,
            'mixing_beta': 0.2,
            'electron_maxstep': 200,
        },
    }
    pseudopotentials = {s: all_pseudopotentials[s] for s in species_list}
    return input_params, pseudopotentials


def build_mg2ni_slab():
    bulk_struct = read('cif/mg2ni-P62.cif')
    slab = bulk_struct * SUPERCELL
    slab.center(vacuum=SLAB_VACUUM, axis=2)
    z = slab.positions[:, 2]
    z_mid = (z.min() + z.max()) / 2
    slab.set_constraint(FixAtoms(mask=(z < z_mid)))
    set_magnetic_moments(slab)
    print(f'  Slab: {len(slab)} atoms, cell c = {slab.cell[2,2]:.1f} A')
    print(f'  Z range: {z.min():.1f} - {z.max():.1f} A, fixed below z = {z_mid:.1f} A')
    return slab, z_mid


if __name__ == '__main__':
    print(f'Settings: supercell={SUPERCELL}, ecutrho={ECUTRHO}, vacuum={SLAB_VACUUM} A\n')

    # --- Calc 1: H2 gas ---
    print('=== Calc 1: H2 ===')
    d = 0.7414
    h2 = Atoms('H2', positions=[[0, 0, 0], [0, 0, d]], cell=[10, 10, 10], pbc=True)
    h2.center()
    inp = {
        'control': {
            'calculation': 'relax', 'prefix': 'h2', 'outdir': './out/',
            'pseudo_dir': pseudo_dir, 'tprnfor': True, 'tstress': True,
            'etot_conv_thr': 1.4e-4, 'forc_conv_thr': 1.0e-4,
            'max_seconds': 27360, 'restart_mode': 'from_scratch',
        },
        'system': {'ecutwfc': 60, 'ecutrho': ECUTRHO, 'occupations': 'fixed'},
        'electrons': {'conv_thr': 1.2e-9},
    }
    write('h2.pwi', h2, format='espresso-in',
          input_data=inp, pseudopotentials={'H': all_pseudopotentials['H']}, kpts=None)
    print('Written: h2.pwi\n')

    # --- Calc 2: Clean slab ---
    print('=== Calc 2: Clean slab ===')
    slab, z_mid = build_mg2ni_slab()
    n_slab = len(slab)
    inp, pp = make_slab_input_params('slab_clean', ['Mg', 'Ni'])
    write('slab_clean.pwi', slab, format='espresso-in',
          input_data=inp, pseudopotentials=pp, kpts=KPTS)
    print(f'Written: slab_clean.pwi ({n_slab} atoms)\n')

    # --- Calc 3: Slab + H ---
    print('=== Calc 3: Slab + H ===')
    slab_h, z_mid_h = build_mg2ni_slab()
    z = slab_h.positions[:, 2]
    z_top = z.max()
    top_mask = z > (z_top - 1.5)
    top_pos = slab_h.positions[top_mask]
    hollow_xy = top_pos[:3, :2].mean(axis=0)
    h_pos = [hollow_xy[0], hollow_xy[1], z_top + 1.6]
    n_s = len(slab_h)
    slab_h += Atoms('H', positions=[h_pos])
    set_magnetic_moments(slab_h)
    fixed = [i for i in range(n_s) if slab_h.positions[i, 2] < z_mid_h]
    slab_h.set_constraint(FixAtoms(indices=fixed))
    inp, pp = make_slab_input_params('slab_H', ['Mg', 'Ni', 'H'])
    write('slab_H.pwi', slab_h, format='espresso-in',
          input_data=inp, pseudopotentials=pp, kpts=KPTS)
    print(f'Written: slab_H.pwi ({len(slab_h)} atoms)\n')

    # --- Phase 2: requires optimized Nb2O5 cluster ---
    try:
        cluster = read('nb2o5_cluster.pwo')
        print(f'=== Optimized Nb2O5 cluster loaded: {len(cluster)} atoms ===\n')
    except FileNotFoundError:
        print('nb2o5_cluster.pwo not found — skipping Calcs 4-7.')
        print('Run Calc 0 first: ./eq_run.sh nb2o5_cluster.pwi')
        exit(0)

    # --- Calc 4: Slab + Nb2O5 ---
    print('=== Calc 4: Slab + Nb2O5 ===')
    slab, z_mid = build_mg2ni_slab()
    n_slab = len(slab)
    z_top = slab.positions[:, 2].max()
    cl = cluster.copy()
    cl.positions[:, 2] += (z_top + 2.2 - cl.positions[:, 2].min())
    slab_center_xy = (slab.cell[0, :2] + slab.cell[1, :2]) / 2
    cl_center_xy = cl.positions[:, :2].mean(axis=0)
    cl.positions[:, 0] += (slab_center_xy - cl_center_xy)[0]
    cl.positions[:, 1] += (slab_center_xy - cl_center_xy)[1]
    slab_nb2o5 = slab + cl
    set_magnetic_moments(slab_nb2o5)
    fixed = [i for i in range(n_slab) if slab_nb2o5.positions[i, 2] < z_mid]
    slab_nb2o5.set_constraint(FixAtoms(indices=fixed))
    inp, pp = make_slab_input_params('slab_Nb2O5', ['Mg', 'Ni', 'Nb', 'O'])
    write('slab_Nb2O5.pwi', slab_nb2o5, format='espresso-in',
          input_data=inp, pseudopotentials=pp, kpts=KPTS)
    print(f'Written: slab_Nb2O5.pwi ({len(slab_nb2o5)} atoms)\n')

    # --- Calc 5: Slab + Nb2O5 + H ---
    print('=== Calc 5: Slab + Nb2O5 + H ===')
    slab_nb2o5_h = slab_nb2o5.copy()
    z_slab_top = slab_nb2o5_h.positions[:n_slab, 2].max()
    cluster_pos = slab_nb2o5_h.positions[n_slab:]
    cluster_center_xy = cluster_pos[:, :2].mean(axis=0)
    h_pos = [cluster_center_xy[0] + 1.5, cluster_center_xy[1], z_slab_top + 1.6]
    slab_nb2o5_h += Atoms('H', positions=[h_pos])
    set_magnetic_moments(slab_nb2o5_h)
    fixed = [i for i in range(n_slab) if slab_nb2o5_h.positions[i, 2] < z_mid]
    slab_nb2o5_h.set_constraint(FixAtoms(indices=fixed))
    inp, pp = make_slab_input_params('slab_Nb2O5_H', ['Mg', 'Ni', 'Nb', 'O', 'H'])
    write('slab_Nb2O5_H.pwi', slab_nb2o5_h, format='espresso-in',
          input_data=inp, pseudopotentials=pp, kpts=KPTS)
    print(f'Written: slab_Nb2O5_H.pwi ({len(slab_nb2o5_h)} atoms)\n')

    # --- Calc 6: Slab + Nb2O5 + Fe ---
    print('=== Calc 6: Slab + Nb2O5 + Fe ===')
    slab_nb2o5_fe = slab_nb2o5.copy()
    nb1_pos = slab_nb2o5_fe.positions[n_slab]
    z_slab_top = slab_nb2o5_fe.positions[:n_slab, 2].max()
    fe_pos = [nb1_pos[0] + 2.0, nb1_pos[1] + 1.5, z_slab_top + 2.0]
    slab_nb2o5_fe += Atoms('Fe', positions=[fe_pos])
    set_magnetic_moments(slab_nb2o5_fe)
    fixed = [i for i in range(n_slab) if slab_nb2o5_fe.positions[i, 2] < z_mid]
    slab_nb2o5_fe.set_constraint(FixAtoms(indices=fixed))
    inp, pp = make_slab_input_params('slab_Nb2O5_Fe', ['Mg', 'Ni', 'Nb', 'O', 'Fe'])
    write('slab_Nb2O5_Fe.pwi', slab_nb2o5_fe, format='espresso-in',
          input_data=inp, pseudopotentials=pp, kpts=KPTS)
    print(f'Written: slab_Nb2O5_Fe.pwi ({len(slab_nb2o5_fe)} atoms)\n')

    # --- Calc 7: Slab + Nb2O5 + Fe + H ---
    print('=== Calc 7: Slab + Nb2O5 + Fe + H ===')
    slab_nb2o5_fe_h = slab_nb2o5_fe.copy()
    fe_pos_current = slab_nb2o5_fe_h.positions[-1]
    z_slab_top = slab_nb2o5_fe_h.positions[:n_slab, 2].max()
    h_pos = [fe_pos_current[0] + 0.5, fe_pos_current[1] - 0.5, z_slab_top + 1.6]
    slab_nb2o5_fe_h += Atoms('H', positions=[h_pos])
    set_magnetic_moments(slab_nb2o5_fe_h)
    fixed = [i for i in range(n_slab) if slab_nb2o5_fe_h.positions[i, 2] < z_mid]
    slab_nb2o5_fe_h.set_constraint(FixAtoms(indices=fixed))
    inp, pp = make_slab_input_params('slab_Nb2O5_Fe_H', ['Mg', 'Ni', 'Nb', 'O', 'Fe', 'H'])
    write('slab_Nb2O5_Fe_H.pwi', slab_nb2o5_fe_h, format='espresso-in',
          input_data=inp, pseudopotentials=pp, kpts=KPTS)
    print(f'Written: slab_Nb2O5_Fe_H.pwi ({len(slab_nb2o5_fe_h)} atoms)\n')

    print('--- Done ---')
    print(f'All inputs generated: supercell={SUPERCELL}, ecutrho={ECUTRHO}')
