import subprocess
import re
import pandas as pd

def run_energy_script():
    """Executes energy.sh and captures its output."""
    try:
        result = subprocess.check_output(['./energy.sh'], text=True)
        return result
    except Exception as e:
        print(f"Error: Could not run ./energy.sh. Details: {e}")
        return None

def compute_adsorption(raw_output):
    """Parse energies and compute H adsorption energy for each system.

    E_ads = E(slab+adsorbates+H) - E(slab+adsorbates) - (n/2)*E(H2_gas)
    """
    RY_TO_EV = 13.6057
    RY_TO_KJMOL = 1312.75

    pattern = r"(\S+\.pwo)\s+(.+?)\s+(-?\d+\.\d+)\s+Ry"
    matches = re.findall(pattern, raw_output)
    data = {m[0]: float(m[2]) for m in matches}

    if 'h2.pwo' not in data:
        print("Error: 'h2.pwo' not found in results.")
        return None

    e_h2 = data['h2.pwo']

    # (Label, slab+H file, slab-ref file, n_H atoms added)
    mappings = [
        ("Baseline: Mg2Ni + H",     "slab_H.pwo",           "slab_clean.pwo",    1),
        ("Nb2O5 catalyst: + H",     "slab_Nb2O5_H.pwo",     "slab_Nb2O5.pwo",    1),
        ("Nb2O5+Fe catalyst: + H",  "slab_Nb2O5_Fe_H.pwo",  "slab_Nb2O5_Fe.pwo", 1),
    ]

    rows = []
    for label, hyd_file, ref_file, n_h in mappings:
        if hyd_file in data and ref_file in data:
            e_ads_ry = data[hyd_file] - data[ref_file] - (n_h / 2) * e_h2
            rows.append({
                "System": label,
                "E_ads (Ry)":     f"{e_ads_ry:.6f}",
                "E_ads (eV)":     f"{e_ads_ry * RY_TO_EV:.4f}",
                "E_ads (kJ/mol)": f"{e_ads_ry * RY_TO_KJMOL:.2f}",
            })
        else:
            missing = [f for f in (hyd_file, ref_file) if f not in data]
            rows.append({
                "System": label,
                "E_ads (Ry)": f"MISSING: {', '.join(missing)}",
                "E_ads (eV)": "",
                "E_ads (kJ/mol)": "",
            })

    return pd.DataFrame(rows)

if __name__ == "__main__":
    raw_text = run_energy_script()

    if raw_text:
        print(raw_text)
        df = compute_adsorption(raw_text)

        if df is not None and not df.empty:
            print("\n--- H ADSORPTION ENERGIES ---")
            print("E_ads = E(slab+H) - E(slab) - (n/2)*E(H2_gas)\n")

            col_widths = {col: max(df[col].astype(str).map(len).max(), len(col)) + 2
                          for col in df.columns}
            header = "".join(col.ljust(col_widths[col]) for col in df.columns)
            print(header)

            for _, row in df.iterrows():
                print("".join(str(row[col]).ljust(col_widths[col]) for col in df.columns))
        else:
            print("No results to display.")
