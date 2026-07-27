import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as const

# ==========================================
# PART 1: Planck's Black Body Radiation
# ==========================================

def planck_spectrum(wavelength, T):
    """Calculates the spectral radiance using Planck's Law."""
    h = const.h
    c = const.c
    k = const.k

    numerator = 2.0 * h * c**2
    exponent = (h * c) / (wavelength * k * T)
    denominator = (wavelength**5) * (np.exp(exponent) - 1.0)

    return numerator / denominator

# Generate an array of wavelengths from 100 nm to 3000 nm
wavelengths = np.linspace(100e-9, 3000e-9, 1000)
temperatures_bb = [4000, 5000, 6000] # Temperatures in Kelvin

plt.figure(figsize=(10, 5))

for T in temperatures_bb:
    radiance = planck_spectrum(wavelengths, T)
    # Convert wavelengths to nm for a cleaner x-axis
    plt.plot(wavelengths * 1e9, radiance, label=f'T = {T} K')

plt.title("Planck's Black Body Radiation Spectrum")
plt.xlabel("Wavelength (nm)")
plt.ylabel("Spectral Radiance (W/m$^3$/sr)")
plt.legend()
plt.grid(True)
plt.show()

# ==========================================
# PART 2: Einstein's Model of Heat Capacity
# ==========================================

def einstein_heat_capacity(T, theta_E):
    """Calculates molar heat capacity using Einstein's model."""
    R = const.R
    x = theta_E / T

    # Avoid division by zero at T=0
    # Add a small epsilon to T if necessary, but starting T at 10K avoids this
    Cv = 3 * R * (x**2) * np.exp(x) / (np.exp(x) - 1)**2
    return Cv

# Approximate Einstein temperatures (in Kelvin) for the requested crystals
einstein_temps = {
    'Gold (Au)': 170,
    'Copper (Cu)': 240,
    'Iron (Fe)': 300
}

# Generate an array of temperatures from 10 K to 1000 K
temperatures_hc = np.linspace(10, 1000, 500)

plt.figure(figsize=(10, 5))

for crystal, theta in einstein_temps.items():
    Cv = einstein_heat_capacity(temperatures_hc, theta)
    plt.plot(temperatures_hc, Cv, label=f'{crystal} ($\\Theta_E$ = {theta} K)')

# Plot the Dulong-Petit classic limit (3R) for comparison
dulong_petit = 3 * const.R
plt.axhline(y=dulong_petit, color='black', linestyle='--', label='Dulong-Petit Limit (3R)')

plt.title("Einstein's Model of Molar Heat Capacity")
plt.xlabel("Temperature (K)")
plt.ylabel("Molar Heat Capacity $C_V$ (J/mol·K)")
plt.legend()
plt.grid(True)
plt.show()
