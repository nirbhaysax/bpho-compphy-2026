"""
Task 10: Hydrogenic Orbitals 2D & 3D
====================================
Computes and visualizes the probability density |psi|^2 of hydrogenic atomic orbitals
for given quantum numbers (n, l, m) using analytical wavefunctions and SciPy.
"""

import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.special import genlaguerre as gen_laguerre, sph_harm_y
import scipy.constants as const

from bpho_theme import apply_theme
T = apply_theme()


def radial_wavefunction(n, l, r, Z=1.0):
    """Compute the radial part R_{n,l}(r) of the hydrogenic wavefunction."""
    a0 = const.physical_constants['Bohr radius'][0] * 1e10  # Bohr radius in Angstroms
    rho = (2.0 * Z * r) / (n * a0)

    # Normalization constant
    prefactor = np.sqrt(
        (2.0 * Z / (n * a0))**3 *
        math.factorial(n - l - 1) /
        (2.0 * n * math.factorial(n + l))
    )

    # Associated Laguerre polynomial L_{n-l-1}^{2l+1}(rho)
    laguerre = gen_laguerre(n - l - 1, 2 * l + 1)(rho)

    R = prefactor * (rho ** l) * np.exp(-rho / 2.0) * laguerre
    return R


def wavefunction(n, l, m, x, y, z, Z=1.0):
    """Compute the full wavefunction psi_{n,l,m}(x, y, z)."""
    r = np.sqrt(x**2 + y**2 + z**2)
    # Avoid division by zero at origin
    r_safe = np.where(r == 0.0, 1e-12, r)

    # Polar angle (colatitude) theta in [0, pi]
    theta = np.arccos(np.clip(z / r_safe, -1.0, 1.0))
    # Azimuthal angle phi in [0, 2pi]
    phi = np.arctan2(y, x)

    R = radial_wavefunction(n, l, r_safe, Z)

    # sph_harm_y(l, m, theta, phi): l=degree, m=order, theta=colatitude, phi=azimuthal
    Y = sph_harm_y(l, m, theta, phi)

    psi = R * Y
    return psi


def main():
    n, l, m = 3, 2, -2
    Z = 1.0

    print(f"Calculating Hydrogenic Orbital for n={n}, l={l}, m={m}, Z={Z}...")

    # ── 2D slice (z = 0 plane) ─────────────────────────────────
    lim = 12.0
    resolution_2d = 250
    x = np.linspace(-lim, lim, resolution_2d)
    y = np.linspace(-lim, lim, resolution_2d)
    X2, Y2 = np.meshgrid(x, y)
    Z2 = np.zeros_like(X2)

    psi_2d = wavefunction(n, l, m, X2, Y2, Z2, Z)
    prob_2d = np.abs(psi_2d)**2

    # ── 3D volumetric grid (coarser for performance) ────────────
    res_3d = 28
    x3 = np.linspace(-lim, lim, res_3d)
    y3 = np.linspace(-lim, lim, res_3d)
    z3 = np.linspace(-lim, lim, res_3d)
    X3, Y3, Z3 = np.meshgrid(x3, y3, z3, indexing='ij')

    psi_3d = wavefunction(n, l, m, X3, Y3, Z3, Z)
    prob_3d = np.abs(psi_3d)**2

    # Keep only high-probability points to reveal orbital shape
    threshold = np.max(prob_3d) * 0.05
    mask = prob_3d > threshold

    x_pts = X3[mask]
    y_pts = Y3[mask]
    z_pts = Z3[mask]
    c_pts = prob_3d[mask]

    n_visible = x_pts.size
    print(f"  3D points after filtering: {n_visible} / {X3.size} ({100 * n_visible / X3.size:.1f}%)")

    # ── Plotting ───────────────────────────────────────────────
    fig = plt.figure(figsize=(14, 7))

    # Panel 1: 2D probability density slice
    ax1 = fig.add_subplot(121)
    im = ax1.imshow(prob_2d, extent=[-lim, lim, -lim, lim],
                    origin='lower', cmap='plasma')
    ax1.set_title(f"z = 0 plane | Z={Z} | n={n}, l={l}, m={m}",
                  fontsize=12, fontweight='bold')
    ax1.set_xlabel("x / Angstroms")
    ax1.set_ylabel("y / Angstroms")
    cbar1 = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
    cbar1.set_label("Probability Density")

    # Panel 2: 3D scatter
    ax2 = fig.add_subplot(122, projection='3d')
    sc = ax2.scatter(x_pts, y_pts, z_pts, c=c_pts, cmap='plasma',
                     marker='o', s=8, alpha=0.7,
                     edgecolors='none', linewidth=0)
    ax2.set_title(f"3D Orbital (n={n}, l={l}, m={m})",
                  fontsize=12, fontweight='bold')
    ax2.set_xlabel("x / Angstroms")
    ax2.set_ylabel("y / Angstroms")
    ax2.set_zlabel("z / Angstroms")
    cbar2 = fig.colorbar(sc, ax=ax2, fraction=0.046, pad=0.04, shrink=0.7)
    cbar2.set_label("Probability Density")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()