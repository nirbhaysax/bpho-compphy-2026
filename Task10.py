"""
Task 10: Hydrogenic Orbitals 2D & 3D (Interactive Selector)
===========================================================
Computes and visualizes the probability density |psi|^2 of hydrogenic atomic orbitals
with interactive Matplotlib sliders for n, l, m, and zoom. Includes a view reset.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import math
from scipy.special import genlaguerre as gen_laguerre, sph_harm_y
import scipy.constants as const

from bpho_theme import apply_theme
CMAP = apply_theme()

# Hoist constant evaluation outside of repetitive loops
A0 = const.physical_constants['Bohr radius'][0] * 1e10  # Bohr radius in Angstroms


def cart2sph(x, y, z):
    """Pre-compute spherical coordinates to avoid redundant trigonometric calculations."""
    r = np.sqrt(x**2 + y**2 + z**2)
    r_safe = np.where(r == 0.0, 1e-12, r)
    theta = np.arccos(np.clip(z / r_safe, -1.0, 1.0))
    phi = np.arctan2(y, x)
    return r_safe, theta, phi


def radial_wavefunction(n, l, r_safe, Z=1.0):
    """Compute the radial part R_{n,l}(r) of the hydrogenic wavefunction."""
    rho = (2.0 * Z * r_safe) / (n * A0)

    # Normalization constant
    prefactor = np.sqrt(
        (2.0 * Z / (n * A0))**3 *
        math.factorial(n - l - 1) /
        (2.0 * n * math.factorial(n + l))
    )

    # Associated Laguerre polynomial L_{n-l-1}^{2l+1}(rho)
    laguerre = gen_laguerre(n - l - 1, 2 * l + 1)(rho)

    R = prefactor * (rho ** l) * np.exp(-rho / 2.0) * laguerre
    return R


def wavefunction(n, l, m, r_safe, theta, phi, Z=1.0):
    """Compute the full wavefunction psi_{n,l,m}(r, theta, phi)."""
    R = radial_wavefunction(n, l, r_safe, Z)
    Y = sph_harm_y(l, m, theta, phi)

    psi = R * Y
    return psi


def main():
    # Initial quantum numbers and view parameters
    init_n, init_l, init_m = 3, 2, -2
    init_zoom = 1.0
    Z = 1.0

    # Matplotlib 3D Default View Angles
    DEFAULT_ELEV = 30
    DEFAULT_AZIM = -60

    # ── Pre-calculate Scaled Grids for all 'n' ─────────────────────────
    grid_cache = {}
    for n_val in range(1, 6):
        lim = 1.3 * (n_val ** 2) / Z

        # 2D Grids
        x2 = np.linspace(-lim, lim, 250)
        y2 = np.linspace(-lim, lim, 250)
        X2, Y2 = np.meshgrid(x2, y2)
        Z2 = np.zeros_like(X2)
        r2, theta2, phi2 = cart2sph(X2, Y2, Z2)

        # 3D Grids
        x3 = np.linspace(-lim, lim, 26)
        y3 = np.linspace(-lim, lim, 26)
        z3 = np.linspace(-lim, lim, 26)
        X3, Y3, Z3 = np.meshgrid(x3, y3, z3, indexing='ij')
        r3, theta3, phi3 = cart2sph(X3, Y3, Z3)

        grid_cache[n_val] = {
            'lim': lim,
            '2d': (X2, Y2, r2, theta2, phi2),
            '3d': (X3, Y3, Z3, r3, theta3, phi3)
        }

    # Extract initial grids
    init_grids = grid_cache[init_n]
    init_lim = init_grids['lim']
    _, _, r2_init, theta2_init, phi2_init = init_grids['2d']
    X3_init, Y3_init, Z3_init, r3_init, theta3_init, phi3_init = init_grids['3d']

    # Setup figure layout with expanded bottom margin for extra UI elements
    fig = plt.figure(figsize=(14, 9))
    plt.subplots_adjust(bottom=0.35)

    # Panel 1: 2D slice
    ax1 = fig.add_subplot(121)

    psi_2d = wavefunction(init_n, init_l, init_m, r2_init, theta2_init, phi2_init, Z)
    prob_2d = np.abs(psi_2d)**2

    im = ax1.imshow(prob_2d, extent=[-init_lim, init_lim, -init_lim, init_lim],
                    origin='lower', cmap='plasma')
    ax1.set_title(f"z = 0 plane | Z={Z} | n={init_n}, l={init_l}, m={init_m}\nBounds: ±{init_lim:.1f}Å",
                  fontsize=12, fontweight='bold')
    ax1.set_xlabel("x / Angstroms")
    ax1.set_ylabel("y / Angstroms")
    cbar1 = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
    cbar1.set_label("Probability Density")

    # Panel 2: 3D scatter
    ax2 = fig.add_subplot(122, projection='3d')
    ax2.view_init(elev=DEFAULT_ELEV, azim=DEFAULT_AZIM)

    psi_3d = wavefunction(init_n, init_l, init_m, r3_init, theta3_init, phi3_init, Z)
    prob_3d = np.abs(psi_3d)**2

    threshold = np.max(prob_3d) * 0.02 if np.max(prob_3d) > 0 else 1e-9
    mask = prob_3d > threshold

    sc = ax2.scatter(X3_init[mask], Y3_init[mask], Z3_init[mask], c=prob_3d[mask],
                     cmap='plasma', marker='o', s=15, alpha=0.7, edgecolors='none', linewidth=0)
    ax2.set_title(f"3D Orbital (n={init_n}, l={init_l}, m={init_m})\nBounds: ±{init_lim:.1f}Å",
                  fontsize=12, fontweight='bold')
    ax2.set_xlabel("x / Angstroms")
    ax2.set_ylabel("y / Angstroms")
    ax2.set_zlabel("z / Angstroms")
    cbar2 = fig.colorbar(sc, ax=ax2, fraction=0.046, pad=0.04, shrink=0.7)
    cbar2.set_label("Probability Density")
    ax2.set_xlim([-init_lim, init_lim])
    ax2.set_ylim([-init_lim, init_lim])
    ax2.set_zlim([-init_lim, init_lim])

    # ── Sliders & Button Setup ─────────────────────────────────
    slider_bg = '#2a2a2a'

    # UI Element Axes
    ax_n = plt.axes([0.25, 0.22, 0.50, 0.03], facecolor=slider_bg)
    ax_l = plt.axes([0.25, 0.17, 0.50, 0.03], facecolor=slider_bg)
    ax_m = plt.axes([0.25, 0.12, 0.50, 0.03], facecolor=slider_bg)
    ax_zoom = plt.axes([0.25, 0.07, 0.50, 0.03], facecolor=slider_bg)
    ax_reset = plt.axes([0.45, 0.02, 0.10, 0.03])

    # Widgets
    s_n = Slider(ax_n, 'n (Principal)', 1, 5, valinit=init_n, valfmt='%d', valstep=1)
    s_l = Slider(ax_l, 'l (Angular)', 0, 4, valinit=init_l, valfmt='%d', valstep=1)
    s_m = Slider(ax_m, 'm (Magnetic)', -4, 4, valinit=init_m, valfmt='%d', valstep=1)
    s_zoom = Slider(ax_zoom, 'Zoom', 0.5, 3.0, valinit=init_zoom, valfmt='%.1fx')
    btn_reset = Button(ax_reset, 'Reset 3D Angle')

    def update(val):
        nonlocal sc

        n = int(s_n.val)
        l = int(s_l.val)
        m = int(s_m.val)
        zoom = s_zoom.val

        # Enforce valid quantum number constraints physically
        if l >= n:
            l = n - 1
            s_l.set_val(l)
        if abs(m) > l:
            m = l if m > 0 else -l
            s_m.set_val(m)

        # Fetch the pre-computed dynamically scaled grid for this specific 'n'
        grids = grid_cache[n]
        base_lim = grids['lim']
        _, _, r2, theta2, phi2 = grids['2d']
        X3, Y3, Z3, r3, theta3, phi3 = grids['3d']

        # Determine limits based on the zoom slider
        view_lim = base_lim / zoom

        # Recalculate wavefunctions
        p2d = np.abs(wavefunction(n, l, m, r2, theta2, phi2, Z))**2
        p3d = np.abs(wavefunction(n, l, m, r3, theta3, phi3, Z))**2

        # Update 2D plot (extent strictly matches pre-computed data physical size)
        im.set_data(p2d)
        im.set_extent([-base_lim, base_lim, -base_lim, base_lim])
        im.set_clim(vmin=p2d.min(), vmax=p2d.max() if p2d.max() > 0 else 1)

        # Apply Zoom clipping visually
        ax1.set_xlim(-view_lim, view_lim)
        ax1.set_ylim(-view_lim, view_lim)
        ax1.set_title(f"z = 0 plane | Z={Z} | n={n}, l={l}, m={m}\nBounds: ±{view_lim:.1f}Å",
                      fontsize=12, fontweight='bold')

        # Update 3D plot and axis limits
        sc.remove()

        thresh = np.max(p3d) * 0.02 if np.max(p3d) > 0 else 1e-9
        msk = p3d > thresh

        sc = ax2.scatter(X3[msk], Y3[msk], Z3[msk], c=p3d[msk], cmap='plasma',
                         marker='o', s=15, alpha=0.7, edgecolors='none', linewidth=0)

        # Apply Zoom clipping visually
        ax2.set_xlim([-view_lim, view_lim])
        ax2.set_ylim([-view_lim, view_lim])
        ax2.set_zlim([-view_lim, view_lim])
        ax2.set_title(f"3D Orbital (n={n}, l={l}, m={m})\nBounds: ±{view_lim:.1f}Å",
                      fontsize=12, fontweight='bold')

        fig.canvas.draw_idle()

    def reset_view(event):
        """Reset the 3D plot camera angle to defaults."""
        ax2.view_init(elev=DEFAULT_ELEV, azim=DEFAULT_AZIM)
        fig.canvas.draw_idle()

    # Event listeners
    s_n.on_changed(update)
    s_l.on_changed(update)
    s_m.on_changed(update)
    s_zoom.on_changed(update)
    btn_reset.on_clicked(reset_view)

    plt.show()


if __name__ == "__main__":
    main()
