import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# Note: This script is for the case with curved edges for the nanosheets. The data in the csv file should look as follows:
# Vg (for Transfer Characteristics), Id (for transfer characteristics for Vd = 0.025), Id (for transfer characteristics for Vd = 1.2),Vd (for Output Characteristics),Id (for Output Characteristics Vg = 0.7),Id (for Output Characteristics Vg = 1.0),Id (for Output Characteristics Vg = 1.5)
# 0.025,4.5015094e-13,1.0585843e-12,0,-8.1553155e-20,-7.4763338e-20,2.1283064e-19
# 0.05,1.1060495e-12,2.5791901e-12,0.025,9.9678928e-06,1.1628133e-05,1.2390047e-05

# ------------------------------------------------------------------

# ----------------------------
# Load and clean CSV
# ----------------------------
def load_clean_csv(file):
    df = pd.read_csv(file, skipinitialspace=True)
    if len(df.columns) == 1:
        df = pd.read_csv(file, sep=r'\t+|\s{2,}', engine='python')
    df.columns = df.columns.str.strip()
    df = df.replace("'", "", regex=True)
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.dropna(how="all")
    return df

# Load the new v5 data file
df = load_clean_csv("All_NS_v5.csv")

# ----------------------------
# Transfer characteristics
# ----------------------------
col_Vg = "Vg (for Transfer Characteristics)"
col_Id_lin = "Id (for transfer characteristics for Vd = 0.025)"
col_Id_sat = "Id (for transfer characteristics for Vd = 1.2)"

Vgs_lin = df[col_Vg].dropna().values
Id_lin = df[col_Id_lin].dropna().values

Vgs_sat = df[col_Vg].dropna().values
Id_sat = df[col_Id_sat].dropna().values

n = min(len(Vgs_lin), len(Id_lin))
Vgs_lin = Vgs_lin[:n]
Id_lin = Id_lin[:n]

n = min(len(Vgs_sat), len(Id_sat))
Vgs_sat = Vgs_sat[:n]
Id_sat = Id_sat[:n]

# ----------------------------
# Device Geometry & Effective Width
# ----------------------------
N_sheets = 3
W_sheet_um = 0.010  
T_sheet_um = 0.005  
L_g_um = 0.007  # Gate Length (adjust if your NSFET length is different!)

# For a GAA Nanosheet, effective width is the total perimeter of all sheets
W_eff_um = N_sheets * 2 * (W_sheet_um + T_sheet_um)

# ----------------------------
# Constant Current Vth Extraction & gm
# ----------------------------
# Standard industry critical current (100 nA)
I_crit = 1e-7  

# Calculate target current scaled to device dimensions
I_target = I_crit * (W_eff_um / L_g_um)

Id_lin_abs = np.abs(Id_lin)
Id_sat_abs = np.abs(Id_sat)

# Use np.interp to find exact Vgs at I_target
sort_idx_lin = np.argsort(Id_lin_abs)
sort_idx_sat = np.argsort(Id_sat_abs)

Vth_lin = np.interp(I_target, Id_lin_abs[sort_idx_lin], Vgs_lin[sort_idx_lin])
Vth_sat = np.interp(I_target, Id_sat_abs[sort_idx_sat], Vgs_sat[sort_idx_sat])

# gm extraction (still needed for performance metrics table)
gm_lin = np.gradient(Id_lin, Vgs_lin)
gm_max = np.nanmax(gm_lin)

gm_sat = np.gradient(Id_sat, Vgs_sat)
gm_sat_max = np.nanmax(gm_sat)

# ----------------------------
# Subthreshold Swing & DIBL
# ----------------------------
Id_pos = np.abs(Id_sat)
mask = Id_pos > 1e-14
Vgs_sub = Vgs_sat[mask]
Id_sub = Id_pos[mask]

logId = np.log10(Id_sub)
slope = np.gradient(logId, Vgs_sub)
SS_mV = (1 / np.max(slope)) * 1000

Vd_lin = 0.025
Vd_sat = 1.2
DIBL = (abs(Vth_lin - Vth_sat)*1000)/(Vd_sat - Vd_lin)

# ----------------------------
# Ion / Ioff
# ----------------------------
VDD = 1.2
Ion = Id_sat[np.argmin(np.abs(Vgs_sat - VDD))]
Ioff = Id_sat[np.argmin(np.abs(Vgs_sat - 0))]
Ion_Ioff = Ion/Ioff

# ----------------------------
# Output Characteristics & gd
# ----------------------------
col_Vd_out = "Vd (for Output Characteristics)"
col_Id_out_07 = "Id (for Output Characteristics Vg = 0.7)"
col_Id_out_10 = "Id (for Output Characteristics Vg = 1.0)"
col_Id_out_15 = "Id (for Output Characteristics Vg = 1.5)"

Vds = df[col_Vd_out].dropna().values
Id_out_07 = df[col_Id_out_07].dropna().values
Id_out_10 = df[col_Id_out_10].dropna().values
Id_out_15 = df[col_Id_out_15].dropna().values

n_out = min(len(Vds), len(Id_out_07), len(Id_out_10), len(Id_out_15))
Vds = Vds[:n_out]
Id_out_07 = Id_out_07[:n_out]
Id_out_10 = Id_out_10[:n_out]
Id_out_15 = Id_out_15[:n_out]

# gd_sat extracted from the curves
gd = np.gradient(Id_out_10, Vds)
gd_sat = np.mean(gd[-10:])

gd0 = np.gradient(Id_out_07, Vds)
gd0_sat = np.mean(gd0[-10:])

gd2 = np.gradient(Id_out_15, Vds)
gd2_sat = np.mean(gd2[-10:])

# ----------------------------
# Normalizations & Conversions
# ----------------------------
# Current conversions (A to mA/um)
Ion_norm = (Ion * 1e3) / W_eff_um
Ioff_norm = (Ioff * 1e3) / W_eff_um

# Transconductance conversions (S to mS/um)
gm_max_lin_norm = (gm_max * 1e3) / W_eff_um
gm_max_sat_norm = (gm_sat_max * 1e3) / W_eff_um
gd_sat_norm = (gd_sat * 1e3) / W_eff_um
gd0_sat_norm = (gd0_sat * 1e3) / W_eff_um
gd2_sat_norm = (gd2_sat * 1e3) / W_eff_um

# ----------------------------
# Save Results to .txt
# ----------------------------
results_text = f"""Extracted Nanosheet FET Parameters
Note: This is for the case with curved edges for the nanosheets.

gm_max_lin            = {gm_max:.3e} (A/V) = {gm_max_lin_norm:.3e} (mS/um)
gm_max_sat            = {gm_sat_max:.3e} (A/V) = {gm_max_sat_norm:.3e} (mS/um)
Vth_lin               = {Vth_lin:.3f} (V)
Vth_sat               = {Vth_sat:.3f} (V)
Subthreshold Swing    = {SS_mV:.3f} (mV/dec)
DIBL                  = {DIBL:.3f} (mV/V)
gd_sat (Vg=1.0V)      = {gd_sat:.3e} (S) = {gd_sat_norm:.3e} (mS/um)
Ion                   = {Ion:.3e} (A) = {Ion_norm:.3f} (mA/um)
Ioff                  = {Ioff:.3e} (A) = {Ioff_norm:.3e} (mA/um)
Ion/Ioff              = {Ion_Ioff:.3e}
"""

with open("Extracted_Parameters_v5_OK.txt", "w") as f:
    f.write(results_text)

print("Extraction complete. Results saved to 'Extracted_Parameters_v5_OK.txt'")

# ----------------------------
# Plots
# ----------------------------

# Window 1: Transfer + gm for Vd = 0.025V
fig1, ax1 = plt.subplots(figsize=(8, 6))
ax1.plot(Vgs_lin, Id_lin, 'b-', linewidth=2, label="Id (Linear)")
ax1.set_xlabel("Vgs (V)")
ax1.set_ylabel("Id (A)", color='b')
ax1.tick_params(axis='y', labelcolor='b')
ax1.set_title("Transfer Characteristic & gm (Vd = 0.025V)")
ax1.grid(True)

ax2 = ax1.twinx()
ax2.plot(Vgs_lin, gm_lin, 'r--', linewidth=2, label="gm")
ax2.set_ylabel("gm (S)", color='r')
ax2.tick_params(axis='y', labelcolor='r')
fig1.tight_layout()

# Window 2: Transfer + gm for Vd = 1.2V
fig2, ax3 = plt.subplots(figsize=(8, 6))
ax3.plot(Vgs_sat, Id_sat, 'b-', linewidth=2, label="Id (Sat)")
ax3.set_xlabel("Vgs (V)")
ax3.set_ylabel("Id (A)", color='b')
ax3.tick_params(axis='y', labelcolor='b')
ax3.set_title("Transfer Characteristic & gm (Vd = 1.2V)")
ax3.grid(True)

ax4 = ax3.twinx()
ax4.plot(Vgs_sat, gm_sat, 'r--', linewidth=2, label="gm")
ax4.set_ylabel("gm (S)", color='r')
ax4.tick_params(axis='y', labelcolor='r')
fig2.tight_layout()

# Window 3: Output Characteristics with Extrapolation
fig3, ax5 = plt.subplots(figsize=(8, 6))
colors = ['g', 'b', 'r']
labels = ['Vg = 0.7V', 'Vg = 1.0V', 'Vg = 1.5V']
Id_outs = [Id_out_07, Id_out_10, Id_out_15]

for Id_out, color, label in zip(Id_outs, colors, labels):
    ax5.plot(Vds, Id_out, color=color, linewidth=2, label=label)
    
    if len(Vds) > 10:
        poly = np.polyfit(Vds[-10:], Id_out[-10:], 1)
        extrap_line = np.poly1d(poly)(Vds)
        ax5.plot(Vds, extrap_line, color=color, linestyle='--', alpha=0.5)

ax5.set_xlabel("Vds (V)")
ax5.set_ylabel("Id (A)")
ax5.set_title("Output Characteristics with Saturation Extrapolations")
ax5.legend()
ax5.grid(True)
fig3.tight_layout()

plt.show()
