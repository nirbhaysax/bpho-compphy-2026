import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import scipy.constants as const

from bpho_theme import apply_theme
T = apply_theme()

# ==========================================
# PART 1: Standard Plot for Various Metals
# ==========================================

# Work functions for common metals (in electron-volts, eV)
work_functions_ev = {
    'Sodium (Na)': 2.36,
    'Zinc (Zn)': 4.31,
    'Copper (Cu)': 4.70,
    'Platinum (Pt)': 6.35
}

# Frequency range: 0 to 3000 THz
frequencies = np.linspace(0, 3000e12, 1000)

# Convert Planck's constant from J*s to eV*s for a direct calculation
h_eV = const.h / const.e

# Custom colors for the 4 metals
metal_colors = [T['DATA'], T['PINK'], T['ORANGE'], T['ACCENT']]

fig, ax = plt.subplots(figsize=(10, 6))

for (metal, phi), color in zip(work_functions_ev.items(), metal_colors):
    # Calculate stopping voltage (V_s = h*f/e - Phi/e)
    V_s = h_eV * frequencies - phi

    # Threshold frequency where V_s = 0
    threshold_f = phi / h_eV

    # Solid line for the physical region (f >= threshold frequency)
    phys_mask = frequencies >= threshold_f
    ax.plot(frequencies[phys_mask] / 1e14, V_s[phys_mask],
            label=f'{metal} ($\\Phi$ = {phi} eV)', linewidth=2.5, color=color)

    # Dashed line for the theoretical extrapolation (f < threshold frequency)
    theo_mask = frequencies < threshold_f
    ax.plot(frequencies[theo_mask] / 1e14, V_s[theo_mask],
            color=color, linestyle='--', alpha=0.5)

# Formatting the plot
ax.axhline(0, color=T['DATA'], linewidth=1.2)
ax.axvline(0, color=T['DATA'], linewidth=1.2)
ax.set_title("Photoelectric Effect: Stopping Voltage vs. Frequency", fontsize=14, fontweight='bold')
ax.set_xlabel(r"Incident Photon Frequency ($10^{14}$ Hz)", fontsize=12)
ax.set_ylabel("Stopping Voltage $V_s$ (V)", fontsize=12)
ax.set_xlim(0, 30)
ax.set_ylim(-7, 6)
ax.legend(loc='upper left')
ax.grid(True, alpha=0.4)

plt.tight_layout()
plt.show()

# ==========================================
# PART 2: EXTENSION - Interactive "App"
# ==========================================

# Set up the figure and axis for the interactive app
fig_app, ax_app = plt.subplots(figsize=(9, 6))
plt.subplots_adjust(bottom=0.25)  # Make room for the slider

# Initial work function
init_phi = 2.0
V_s_app = h_eV * frequencies - init_phi
threshold_f_app = init_phi / h_eV

# Plot initial lines
line_phys, = ax_app.plot(frequencies[frequencies >= threshold_f_app] / 1e14,
                          V_s_app[frequencies >= threshold_f_app],
                          color='blue', linewidth=3)
line_theo, = ax_app.plot(frequencies[frequencies < threshold_f_app] / 1e14,
                          V_s_app[frequencies < threshold_f_app],
                          color='blue', linestyle='--', alpha=0.5)

ax_app.axhline(0, color=T['DATA'], linewidth=1)
ax_app.axvline(0, color=T['DATA'], linewidth=1)
ax_app.set_xlim(0, 30)
ax_app.set_ylim(-8, 6)
ax_app.set_title("Interactive Photoelectric Effect App", fontsize=14, fontweight='bold')
ax_app.set_xlabel(r"Incident Photon Frequency ($10^{14}$ Hz)")
ax_app.set_ylabel("Stopping Voltage $V_s$ (V)")
ax_app.grid(True, alpha=0.3)

# Add the slider
ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor='#2a2a2a')
phi_slider = Slider(
    ax=ax_slider,
    label='Work Function $\\Phi$ (eV)',
    valmin=1.0,
    valmax=7.0,
    valinit=init_phi,
    color=T['ACCENT']
)

# Function to update the plot when the slider changes
def update(val):
    current_phi = phi_slider.val
    new_Vs = h_eV * frequencies - current_phi
    new_threshold = current_phi / h_eV

    # Update physical line data
    line_phys.set_xdata(frequencies[frequencies >= new_threshold] / 1e14)
    line_phys.set_ydata(new_Vs[frequencies >= new_threshold])

    # Update theoretical line data
    line_theo.set_xdata(frequencies[frequencies < new_threshold] / 1e14)
    line_theo.set_ydata(new_Vs[frequencies < new_threshold])

    fig_app.canvas.draw_idle()

phi_slider.on_changed(update)

plt.show()