import numpy as np
import matplotlib.pyplot as plt

from bpho_theme import apply_theme
T = apply_theme()

# ==========================================
# TASK 5: Bohr Model Hydrogen Emission Spectrum
# ==========================================

# Constants
R_E = 13.605693  # Ground state energy of Hydrogen in eV
hc = 1239.84193  # Planck's constant * speed of light in eV*nm

# Dictionary mapping the series name to its final energy level (n_f) and plot color
series_map = {
    'Lyman': (1, T['DATA']),
    'Balmer': (2, T['PINK']),
    'Paschen': (3, T['ACCENT']),
    'Brackett': (4, T['ORANGE']),
    'Pfund': (5, T['DATA'])
}

plt.figure(figsize=(10, 6))

# Plot a faint background curve showing the inverse E = hc/lambda relationship
lambdas_curve = np.linspace(90, 8000, 1000)
energies_curve = hc / lambdas_curve
plt.plot(lambdas_curve, energies_curve, color=T['MUTED'], linestyle='--', zorder=1)

# Calculate and plot the transitions for each series
max_ni = 30  # Calculate up to n=30 to show the series limit clustering

for name, (nf, color) in series_map.items():
    # Array of initial energy levels (from n_f + 1 up to max_ni)
    ni = np.arange(nf + 1, max_ni)
    
    # Calculate photon energies in eV
    energies = R_E * (1/(nf**2) - 1/(ni**2))
    
    # Calculate corresponding wavelengths in nm
    wavelengths = hc / energies
    
    # Plot the specific transition points (using '+' markers as seen in the prompt)
    plt.scatter(wavelengths, energies, color=color, label=name, marker='+', zorder=3)
    
    # Draw vertical dotted lines from each point down to the x-axis
    for w, e in zip(wavelengths, energies):
        plt.vlines(x=w, ymin=0, ymax=e, color=color, linestyle=':', linewidth=1, alpha=0.7, zorder=2)

# Formatting the plot to match the BPhO styling
plt.title("Bohr model of Hydrogenic atom\nphoton emissions: Z = 1", fontweight='bold')
plt.xlabel(r"$\lambda$ /nm")
plt.ylabel("Photon energy /eV")
plt.xlim(0, 8000)
plt.ylim(0, 13.5)
plt.legend(loc='upper right')
plt.grid(True, alpha=0.4, linestyle='--')

plt.tight_layout()
plt.show()