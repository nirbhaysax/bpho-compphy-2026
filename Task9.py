import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as const

# ==========================================
# TASK 9: Compton Scattering Model
# ==========================================

# Physical Constants
h = const.h
m_e = const.m_e
c = const.c
e = const.e

# Compton wavelength of an electron in meters
lambda_c = h / (m_e * c)

# Incident X-ray photon wavelength (e.g., 0.071 nm for Mo K-alpha)
lambda_init = 0.071e-9 

# Photon scattering angle theta from 0 to 180 degrees
theta_deg = np.linspace(0, 180, 500)
theta_rad = np.deg2rad(theta_deg)

# 1. Fractional Wavelength Shift
delta_lambda = lambda_c * (1 - np.cos(theta_rad))
fractional_shift = delta_lambda / lambda_init
lambda_prime = lambda_init + delta_lambda

# 2. Electron Recoil Speed (v/c)
# Incident and scattered photon energies in Joules
E_incident = (h * c) / lambda_init
E_scattered = (h * c) / lambda_prime
E_kinetic = E_incident - E_scattered

# Relativistic velocity calculation
gamma = 1 + (E_kinetic / (m_e * c**2))
v_over_c = np.sqrt(1 - (1 / gamma**2))

# 3. Electron Recoil Angle (phi)
# denominator = (lambda_prime / lambda_init) - cos(theta); can be zero at theta=0
denom = (lambda_prime / lambda_init) - np.cos(theta_rad)
# Use np.where to avoid division by zero at theta=0 (where denom=0, phi -> pi/2)
tan_phi = np.where(np.abs(denom) < 1e-15, np.inf, np.sin(theta_rad) / denom)
phi_rad = np.arctan(tan_phi)
phi_deg = np.rad2deg(phi_rad)

# ==========================================
# Plotting the Results
# ==========================================
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))

# Panel 1: Fractional Wavelength Shift vs Theta
ax1.plot(theta_deg, fractional_shift, color='blue', linewidth=2.5)
ax1.set_title("Fractional Wavelength Shift", fontweight='bold')
ax1.set_xlabel(r"Photon Scattering Angle $\theta$ (degrees)")
ax1.set_ylabel(r"$\Delta\lambda / \lambda$")
ax1.grid(True, linestyle='--', alpha=0.5)

# Panel 2: Electron Recoil Speed vs Theta
ax2.plot(theta_deg, v_over_c, color='red', linewidth=2.5)
ax2.set_title("Electron Recoil Speed", fontweight='bold')
ax2.set_xlabel(r"Photon Scattering Angle $\theta$ (degrees)")
ax2.set_ylabel("Speed ($v/c$)")
ax2.grid(True, linestyle='--', alpha=0.5)

# Panel 3: Electron Recoil Angle vs Theta
ax3.plot(theta_deg, phi_deg, color='green', linewidth=2.5)
ax3.set_title("Electron Recoil Angle $\\phi$", fontweight='bold')
ax3.set_xlabel("Photon Scattering Angle $\theta$ (degrees)")
ax3.set_ylabel(r"Recoil Angle $\phi$ (degrees)")
ax3.grid(True, linestyle='--', alpha=0.5)

plt.suptitle(rf"Compton Scattering Analysis ($\lambda$ = {lambda_init*1e9:.3f} nm)", fontsize=14, fontweight='bold', y=1.03)
plt.tight_layout()
plt.show()