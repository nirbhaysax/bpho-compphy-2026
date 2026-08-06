"""
Task 1: Random Walk Model
==========================
Simulation of multiple 2D random walks. At each of N steps the particle
moves a fixed distance s in a completely random direction from 0 to 2pi.
"""

import numpy as np
import matplotlib.pyplot as plt
from bpho_theme import apply_theme

CMAP = apply_theme()


def random_walk(N, s):
    """Generate a single 2D random walk of N steps with step size s."""
    angles = 2 * np.pi * np.random.rand(N)
    dx = s * np.cos(angles)
    dy = s * np.sin(angles)
    x = np.cumsum(dx)
    y = np.cumsum(dy)
    return np.insert(x, 0, 0), np.insert(y, 0, 0)  # start at origin


# ── Parameters ───────────────────────────────────────────────────
N = 2000        # number of steps per walk
s = 1.0         # step size
num_walks = 6   # how many walkers to overlay

plt.figure(figsize=(10, 10))

for w in range(num_walks):
    x, y = random_walk(N, s)
    # Fade later walks slightly so the ensemble isn't a blur
    alpha_val = 0.85 - w * 0.06
    if w == 0:
        plt.plot(x, y, linewidth=1.0, color=CMAP['ACCENT'], alpha=1.0,
                 label='Random walk')
    else:
        plt.plot(x, y, linewidth=0.7, color=CMAP['ACCENT'], alpha=alpha_val)

# Mark start and end of the first walk for clarity
plt.scatter(x[0], y[0], color=CMAP['DATA'], s=80, zorder=5, label='Start')
plt.scatter(x[-1], y[-1], color=CMAP['PINK'], s=80, zorder=5, label='End')

plt.title(f"2D Random Walk   |   N = {N} steps   step s = {s}   walkers = {num_walks}",
          fontweight='bold')
plt.xlabel("x")
plt.ylabel("y")
plt.axis("equal")
plt.legend(loc='upper right')
plt.grid(True, linestyle=':', alpha=0.3)

plt.tight_layout()
plt.show()