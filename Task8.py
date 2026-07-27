import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# ==========================================
# TASK 8: Quantum Cryptography Visual Calculator
# ==========================================

# Function to calculate mismatch probabilities
def calculate_mismatch(theta, phi):
    """Calculates classical and quantum mismatch probabilities for given angles in radians."""
    delta_theta = np.abs(theta - phi)
    
    # Quantum probability: P_q = sin^2(theta - phi)
    p_quantum = np.sin(delta_theta)**2
    
    # Classical linear local realistic bound
    p_classical = np.minimum(delta_theta / (np.pi / 2), 1.0)
    
    return p_quantum, p_classical

# Set up the figure and layout
fig, (ax_curve, ax_visual) = plt.subplots(1, 2, figsize=(14, 6))
plt.subplots_adjust(bottom=0.25)

# ------------------------------------------
# Panel 1: Probability Curves vs Angle Difference
# ------------------------------------------
angles_rad = np.linspace(0, np.pi/2, 500)
q_curve, c_curve = calculate_mismatch(0, angles_rad)

ax_curve.plot(angles_rad * (180/np.pi), q_curve, color='blue', linewidth=2.5, label='Quantum ($P = \\sin^2\\Delta\\theta$)')
ax_curve.plot(angles_rad * (180/np.pi), c_curve, color='red', linestyle='--', linewidth=2, label='Classical Linear Bound')

# Dynamic points tracking current slider values
point_q, = ax_curve.plot([], [], 'bo', markersize=10, label='Current Quantum State')
point_c, = ax_curve.plot([], [], 'ro', markersize=10, label='Current Classical State')

ax_curve.set_title("Mismatch Probability vs. Angular Difference", fontweight='bold')
ax_curve.set_xlabel(r"Angle Difference $\Delta\theta$ (degrees)")
ax_curve.set_ylabel("Mismatch Probability")
ax_curve.set_xlim(0, 90)
ax_curve.set_ylim(0, 1.05)
ax_curve.legend(loc='upper left')
ax_curve.grid(True, linestyle='--', alpha=0.5)

# ------------------------------------------
# Panel 2: Visual Representation of Detectors
# ------------------------------------------
ax_visual.set_xlim(-1.5, 1.5)
ax_visual.set_ylim(-1.5, 1.5)
ax_visual.set_aspect('equal')
ax_visual.axis('off')
ax_visual.set_title("Detector Polarization Axes", fontweight='bold')

# Draw reference unit circles
circle_a = plt.Circle(( -0.75, 0), 0.7, color='lightgray', fill=False, linestyle='--')
circle_b = plt.Circle((  0.75, 0), 0.7, color='lightgray', fill=False, linestyle='--')
ax_visual.add_patch(circle_a)
ax_visual.add_patch(circle_b)

# Detector polarization axis lines
line_a, = ax_visual.plot([], [], 'g-', linewidth=3, label=r"Detector A ($\theta$)")
line_b, = ax_visual.plot([], [], 'm-', linewidth=3, label=r"Detector B ($\phi$)")
ax_visual.legend(loc='lower center')

# Text box to display live calculated values
text_box = ax_visual.text(-1.4, -1.3, "", fontsize=11, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8))

# ------------------------------------------
# Interactive Sliders Setup
# ------------------------------------------
ax_slider_theta = plt.axes([0.2, 0.12, 0.6, 0.03], facecolor='lightgoldenrodyellow')
ax_slider_phi   = plt.axes([0.2, 0.06, 0.6, 0.03], facecolor='lightgoldenrodyellow')

slider_theta = Slider(ax=ax_slider_theta, label=r'Detector A Angle ($\theta$°)', valmin=0, valmax=90, valinit=0, valstep=1)
slider_phi   = Slider(ax=ax_slider_phi,   label=r'Detector B Angle ($\phi$°)', valmin=0, valmax=90, valinit=45, valstep=1)

def update(val):
    deg_theta = slider_theta.val
    deg_phi = slider_phi.val
    
    rad_theta = np.deg2rad(deg_theta)
    rad_phi = np.deg2rad(deg_phi)
    
    # Calculate probabilities
    pq, pc = calculate_mismatch(rad_theta, rad_phi)
    diff_deg = np.abs(deg_theta - deg_phi)
    
    # Update curve tracker points
    point_q.set_data([diff_deg], [pq])
    point_c.set_data([diff_deg], [pc])
    
    # Update detector vector lines on visual panel
    # Detector A vector (centered at x = -0.75)
    xa = 0.7 * np.cos(rad_theta)
    ya = 0.7 * np.sin(rad_theta)
    line_a.set_data([-0.75 - xa, -0.75 + xa], [-ya, ya])
    
    # Detector B vector (centered at x = 0.75)
    xb = 0.7 * np.cos(rad_phi)
    yb = 0.7 * np.sin(rad_phi)
    line_b.set_data([0.75 - xb, 0.75 + xb], [-yb, yb])
    
    # Update status text box
    text_box.set_text(f"Δθ = {diff_deg}°\nQuantum Mismatch: {pq:.3f}\nClassical Mismatch: {pc:.3f}\nDifference: {pq - pc:+.3f}")
    
    fig.canvas.draw_idle()

slider_theta.on_changed(update)
slider_phi.on_changed(update)

# Initialize with starting values
update(0)

plt.show()