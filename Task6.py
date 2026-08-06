import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import scipy.constants as const

from bpho_theme import apply_theme
CMAP = apply_theme()

# ==========================================
# TASK 6: Electron Diffraction App
# ==========================================

# Constants
h = const.h
m_e = const.m_e
e = const.e

# Graphite atomic spacings (meters)
d1 = 0.123e-9
d2 = 0.213e-9

# Spherical tube radius (meters)
r_tube = 65e-3 

def calculate_diffraction(V):
    """Calculates ring radii and sin(phi/2) for a given voltage."""
    # De Broglie wavelength
    lambda_e = h / np.sqrt(2 * m_e * e * V)
    
    # Scattering angles (phi)
    sin_half_phi1 = lambda_e / (2 * d1)
    sin_half_phi2 = lambda_e / (2 * d2)
    
    phi1 = 2 * np.arcsin(sin_half_phi1)
    phi2 = 2 * np.arcsin(sin_half_phi2)
    
    # Ring radii on the screen (x = r * sin(2*phi))
    x1 = r_tube * np.sin(2 * phi1)
    x2 = r_tube * np.sin(2 * phi2)
    
    return (x1, x2), (sin_half_phi1, sin_half_phi2)

# Set up the figure and grid layout
fig = plt.figure(figsize=(14, 6))
plt.subplots_adjust(bottom=0.25)
ax_screen = fig.add_subplot(121)
ax_graph = fig.add_subplot(122)

# ------------------------------------------
# Panel 1: Phosphor Screen Visualization
# ------------------------------------------
ax_screen.set_facecolor('black')
ax_screen.set_xlim(-0.06, 0.06)
ax_screen.set_ylim(-0.06, 0.06)
ax_screen.set_aspect('equal')
ax_screen.set_title("Phosphor Screen ('Electron Wave' Rings)", color=CMAP['ACCENT'], fontweight='bold')
ax_screen.axis('off')

# Central beam glow
theta = np.linspace(0, 2*np.pi, 500)
ax_screen.plot(0.002 * np.cos(theta), 0.002 * np.sin(theta), color='white', linewidth=4, alpha=0.9)
ax_screen.fill(0.002 * np.cos(theta), 0.002 * np.sin(theta), color='white')

# Initialize the rings
ring1, = ax_screen.plot([], [], color=CMAP['ACCENT'], linewidth=2.5, alpha=0.8)
ring2, = ax_screen.plot([], [], color=CMAP['ACCENT'], linewidth=2.5, alpha=0.8)

# ------------------------------------------
# Panel 2: 1/sqrt(V) vs sin(phi/2) Graph
# ------------------------------------------
# Generate theoretical lines for V ranging from 1kV to 5kV
V_range = np.linspace(1000, 5000, 200)
inv_sqrt_V_range = 1 / np.sqrt(V_range)

sin_half_phi1_range = (h / np.sqrt(2 * m_e * e * V_range)) / (2 * d1)
sin_half_phi2_range = (h / np.sqrt(2 * m_e * e * V_range)) / (2 * d2)

ax_graph.plot(sin_half_phi1_range, inv_sqrt_V_range, color=CMAP['DATA'], label='d = 0.123 nm')
ax_graph.plot(sin_half_phi2_range, inv_sqrt_V_range, color=CMAP['PINK'], label='d = 0.213 nm')

# Scatter points to track current voltage on the graph
point1, = ax_graph.plot([], [], 'o', color=CMAP['ACCENT'], markersize=8)
point2, = ax_graph.plot([], [], 'o', color=CMAP['PINK'], markersize=8)

ax_graph.set_title(r"Verification: $1/\sqrt{V}$ vs $\sin(\frac{1}{2}\phi)$", fontweight='bold')
ax_graph.set_xlabel(r"$\sin(\frac{1}{2}\phi)$")
ax_graph.set_ylabel(r"$1/\sqrt{V}$  ($V^{-1/2}$)")
ax_graph.legend()
ax_graph.grid(True, linestyle='--', alpha=0.6)

# ------------------------------------------
# Interactive Slider Setup
# ------------------------------------------
ax_slider = plt.axes([0.2, 0.1, 0.6, 0.04], facecolor='#2a2a2a')
voltage_slider = Slider(
    ax=ax_slider,
    label='Accelerating Voltage (V)',
    valmin=1000,
    valmax=5000,
    valinit=3000,
    valstep=50,
    color=CMAP['ACCENT']
)

def update(val):
    V = voltage_slider.val
    radii, sin_half_phis = calculate_diffraction(V)
    
    # Update Screen Rings
    ring1.set_data(radii[0] * np.cos(theta), radii[0] * np.sin(theta))
    ring2.set_data(radii[1] * np.cos(theta), radii[1] * np.sin(theta))
    
    # Update Graph Points
    current_inv_sqrt_V = 1 / np.sqrt(V)
    point1.set_data([sin_half_phis[0]], [current_inv_sqrt_V])
    point2.set_data([sin_half_phis[1]], [current_inv_sqrt_V])
    
    fig.canvas.draw_idle()

# Initialize plot with starting values
update(3000)

voltage_slider.on_changed(update)
plt.show()