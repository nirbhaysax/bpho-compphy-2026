import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as const

from bpho_theme import apply_theme
T = apply_theme()

# ==========================================
# TASK 7: Particle-in-a-Box & Uncertainty
# ==========================================

# Given parameters matching the reference image
m = 9.1094e-31          # Mass of electron (kg)
L = 0.5e-10             # Width of box (0.5 Angstroms in meters)
h = const.h
hbar = const.hbar

# Position array across the box
x = np.linspace(0, L, 1000)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# ------------------------------------------
# Panel 1: Probability Density vs Position
# ------------------------------------------
n_values = [1, 2, 3]
colors = [T['DATA'], T['ACCENT'], T['PINK']]

for n, color in zip(n_values, colors):
    # Energy calculation in Joules, then converted to eV
    E_joules = (n**2 * h**2) / (8 * m * L**2)
    E_ev = E_joules / const.e

    # Probability density
    psi_sq = (2 / L) * np.sin((n * np.pi * x) / L)**2

    # Plot probability density (x converted to Angstroms for display)
    ax1.plot(x * 1e10, psi_sq, color=color, label=f'n = {n}  E = {E_ev:.4f} eV')

ax1.set_title(f"Particle in a box\nm = {m:.2e} kg", fontweight='bold')
ax1.set_xlabel("x / angstroms")
ax1.set_ylabel("Probability density")
ax1.legend(loc='upper right')
ax1.grid(True, linestyle='--', alpha=0.5)

# ------------------------------------------
# Panel 2: Energy vs Quantum Number n
# ------------------------------------------
n_range = np.arange(1, 11)
energies_ev = (n_range**2 * h**2) / (8 * m * L**2 * const.e)

ax2.plot(n_range, energies_ev, 'wo-', linewidth=2, markersize=6,
         markerfacecolor=T['ACCENT'], markeredgecolor='white')
ax2.set_title("Energy Levels vs Quantum Number", fontweight='bold')
ax2.set_xlabel("Quantum Number (n)")
ax2.set_ylabel("Energy (eV)")
ax2.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()

# ------------------------------------------
# EXTENSION: Uncertainty Principle Verification
# ------------------------------------------
print("--- Heisenberg Uncertainty Principle Verification ($\\Delta x \\Delta p$) ---")
for n in range(1, 6):
    # Analytical calculations for particle in a box
    delta_x = L * np.sqrt(1/12.0 - 1.0 / (2.0 * n**2 * np.pi**2))
    delta_p = (n * np.pi * hbar) / L
    product = delta_x * delta_p
    bound = 0.5 * hbar

    print(f"n = {n}: Δx·Δp = {product:.5e} J·s  |  (1/2)ħ = {bound:.5e} J·s  --> Valid: {product >= bound}")