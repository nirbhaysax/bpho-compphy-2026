import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.special import genlaguerre as gen_laguerre, sph_harm
import scipy.constants as const

# ==========================================
# TASK 10: Hydrogenic Orbitals Visualizer
# ==========================================

# Quantum numbers for the target orbital (e.g., n=3, l=2, m=-2 -> 3dxy-like)
n = 3
l = 2
m = -2
Z = 1  # Atomic number for Hydrogen

# Constants and Bohr radius (meters)
a_0 = 5.29177e-11 

def radial_wavefunction(n, l, r, Z):
    """Calculates the radial part R_nl(r) of the hydrogenic wavefunction."""
    rho = (2.0 * Z * r) / (n * a_0)
    # Normalization constant
    factor = np.sqrt((2.0 * Z / (n * a_0))**3 * math.factorial(n - l - 1) / (2.0 * n * math.factorial(n + l)))
    # Associated Laguerre polynomial L_{n-l-1}^{2l+1}(rho)
    laguerre = gen_laguerre(n - l - 1, 2 * l + 1)(rho)
    return factor * (rho**l) * np.exp(-rho / 2.0) * laguerre

def hydrogen_wavefunction(n, l, m, x, y, z):
    """Calculates the complex spatial wavefunction psi(x, y, z).'"""
    r = np.sqrt(x**2 + y**2 + z**2)
    # Avoid division by zero at origin
    r = np.where(r == 0, 1e-15, r)
    
    # Polar angles (theta: colatitude, phi: azimuth)
    theta = np.arccos(z / r)
    phi = np.arctan2(y, x)
    
    R = radial_wavefunction(n, l, r, Z)
    # scipy sph_harm signature: sph_harm(m, l, phi, theta)
    Y = sph_harm(m, l, phi, theta)
    
    return R * Y

# Setup coordinate grid (in Angstroms, converted to meters for calculation)
lim_angstroms = 8.0
grid_points = 150
x_ang = np.linspace(-lim_angstroms, lim_angstroms, grid_points)
y_ang = np.linspace(-lim_angstroms, lim_angstroms, grid_points)
X, Y = np.meshgrid(x_ang, y_ang)

X_m = X * 1e-10
Y_m = Y * 1e-10
Z_m = np.zeros_like(X_m)  # z = 0 plane slice

# Calculate wavefunction and probability density for 2D slice
psi_2d = hydrogen_wavefunction(n, l, m, X_m, Y_m, Z_m)
prob_density_2d = np.abs(psi_2d)**2

# ==========================================
# Plotting the Results
# ==========================================
fig = plt.figure(figsize=(14, 6))

# Panel 1: 2D Probability Density Slice (z = 0 plane)
ax1 = fig.add_subplot(121)
im = ax1.imshow(prob_density_2d, extent=[-lim_angstroms, lim_angstroms, -lim_angstroms, lim_angstroms], 
                origin='lower', cmap='jet')
ax1.set_title(f"z = 0 plane | Z={Z} | n={n}, l={l}, m={m}", fontweight='bold')
ax1.set_xlabel("x / Angstroms")
ax1.set_ylabel("y / Angstroms")
fig.colorbar(im, ax=ax1, label="Probability Density")

# Panel 2: 3D Volumetric Probability Cloud via 3D Scatter
ax2 = fig.add_subplot(122, projection='3d')

# Generate a 3D spatial grid for the volumetric plot
lim_3d = 6.0
pts_3d = 40
x_3d = np.linspace(-lim_3d, lim_3d, pts_3d)
y_3d = np.linspace(-lim_3d, lim_3d, pts_3d)
z_3d = np.linspace(-lim_3d, lim_3d, pts_3d)
X3, Y3, Z3 = np.meshgrid(x_3d, y_3d, z_3d)

# Convert to meters
psi_3d = hydrogen_wavefunction(n, l, m, X3 * 1e-10, Y3 * 1e-10, Z3 * 1e-10)
prob_3d = np.abs(psi_3d)**2

# Filter points above a threshold to display the orbital shape cleanly
threshold = 0.05 * np.max(prob_3d)
mask = prob_3d > threshold

sc = ax2.scatter(X3[mask], Y3[mask], Z3[mask], c=prob_3d[mask], cmap='jet', marker='o', s=15, alpha=0.6)
ax2.set_title(f"3D Orbital Visualization (n={n}, l={l}, m={m})", fontweight='bold')
ax2.set_xlabel("x in Angstroms")
ax2.set_ylabel("y in Angstroms")
ax2.set_zlabel("z in Angstroms")
fig.colorbar(sc, ax=ax2, shrink=0.6, label="Probability Density")

plt.tight_layout()
plt.show()