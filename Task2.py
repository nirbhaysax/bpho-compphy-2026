"""
Task 2: Brownian Motion Simulation (Optimized with cKDTree)
===========================================================
Models the 2D Brownian motion of a large observable particle (mass M, radius R)
colliding with N smaller particles (mass m, radius r) in random thermal motion.

Small-small particle collisions are accurately resolved using an O(N log N)
spatial partitioning structure (scipy.spatial.cKDTree) for high performance.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button
from scipy.spatial import cKDTree
from bpho_theme import apply_theme

CMAP = apply_theme()

# ── Simulation Settings ───────────────────────────────────────────
# Set to an integer (e.g., 1) for the exact same path every time,
# or set to None for a completely random path on every run.
RANDOM_SEED    = None
rng = np.random.default_rng(RANDOM_SEED)

# ── Physical parameters ───────────────────────────────────────────
N      = 250                      # small particles
T_c    = 100.0                    # temperature  (deg C)
m      = 28.96e-3 / 6.02e23       # small-particle mass  (kg)  ~ air molecule
M      = 10 * m                   # large-particle mass  (kg)
r      = 0.16                     # small-particle radius (nm)
R      = 10 * r                   # large-particle radius (nm)
a      = 7 * R                    # scene size (nm)
C      = 1.0                      # coefficient of restitution
kB     = 1.38e-23                 # Boltzmann constant (J/K)

# ── Derived quantities ────────────────────────────────────────────
v = np.sqrt(3 * kB * (T_c + 273) / m)   # small-particle mean speed (m/s)
v /= 1000.0                        # m/s  ->  nm/ps

Kn = 15.0                          # Knudsen number
dt = 0.02 * Kn * r / v             # timestep (ps)
tmax = 200.0                       # total simulation time (ps)


# ── Collision resolver (Large vs Small) ───────────────────────────
def resolve_collision(X, Y, x_i, y_i, Vx, Vy, vx_i, vy_i):
    """Resolve a single large-small collision if they overlap and approach."""
    dx = x_i - X
    dy = y_i - Y
    d2 = dx*dx + dy*dy
    sumR = R + r
    if d2 > sumR*sumR:
        return Vx, Vy, vx_i, vy_i, X, Y, x_i, y_i

    d = np.sqrt(d2)
    dx /= d
    dy /= d

    # push apart to prevent sticking
    delta = (sumR - d) / 2
    X -= delta * dx
    Y -= delta * dy
    x_i += delta * dx
    y_i += delta * dy

    # relative velocity along the contact normal
    rel_vel = (x_i - X) * dx + (y_i - Y) * dy
    if rel_vel >= 0:
        return Vx, Vy, vx_i, vy_i, X, Y, x_i, y_i

    # perfectly elastic momentum exchange
    Vx_new = Vx + (2 * m / (M + m)) * rel_vel * dx
    Vy_new = Vy + (2 * m / (M + m)) * rel_vel * dy
    vx_new = vx_i - (2 * M / (M + m)) * rel_vel * dx
    vy_new = vy_i - (2 * M / (M + m)) * rel_vel * dy

    return Vx_new, Vy_new, vx_new, vy_new, X, Y, x_i, y_i


# ── Initial conditions ────────────────────────────────────────────
X_big, Y_big = 0.5 * a, 0.5 * a
Vx = Vy = 0.0

# Place small particles uniformly, away from the large one
x = rng.uniform(2 * (r + R), a - 2 * (r + R), N)
y = rng.uniform(2 * (r + R), a - 2 * (r + R), N)
for n in range(N):
    while (x[n] - X_big)**2 + (y[n] - Y_big)**2 < (r + R)**2:
        x[n] = rng.uniform(2 * (r + R), a - 2 * (r + R))
        y[n] = rng.uniform(2 * (r + R), a - 2 * (r + R))

theta0 = 2 * np.pi * rng.random(N)
vx = v * np.cos(theta0)
vy = v * np.sin(theta0)

# ── Time stepping ─────────────────────────────────────────────────
n_steps = int(np.ceil(tmax / dt))
save_every = max(1, n_steps // 180)

frames_sx, frames_sy = [x.copy()], [y.copy()]
frames_bX, frames_bY = [X_big], [Y_big]
frames_t = [0.0]

for step in range(n_steps):
    # Euler step
    X_big += Vx * dt
    Y_big += Vy * dt
    x += vx * dt
    y += vy * dt

    # 1. Wall Collisions (keep small particles inside the box)
    vx = np.where(x < r, np.abs(vx), vx)
    vx = np.where(x > a - r, -np.abs(vx), vx)
    vy = np.where(y < r, np.abs(vy), vy)
    vy = np.where(y > a - r, -np.abs(vy), vy)

    # 2. Large vs Small Collisions (O(N) Vectorized Check)
    dx_arr = x - X_big
    dy_arr = y - Y_big
    d2_arr = dx_arr*dx_arr + dy_arr*dy_arr
    collision_mask = d2_arr < (R + r)**2

    if collision_mask.any():
        indices = np.flatnonzero(collision_mask)
        for i in indices:
            Vx, Vy, vx[i], vy[i], X_big, Y_big, x[i], y[i] = resolve_collision(
                X_big, Y_big, x[i], y[i], Vx, Vy, vx[i], vy[i]
            )

    # 3. Small vs Small Collisions (O(N log N) cKDTree Check)
    tree = cKDTree(np.c_[x, y])
    # Find all pairs whose distance is less than 2*r
    pairs = tree.query_pairs(2 * r)

    if pairs:
        pairs_arr = np.array(list(pairs))
        idx_i, idx_j = pairs_arr[:, 0], pairs_arr[:, 1]

        # Calculate distances and normals
        dx_ss = x[idx_i] - x[idx_j]
        dy_ss = y[idx_i] - y[idx_j]
        dist = np.sqrt(dx_ss**2 + dy_ss**2)

        # Prevent division by zero if particles occupy the exact same space
        dist = np.where(dist == 0, 1e-9, dist)

        nx = dx_ss / dist
        ny = dy_ss / dist

        # Push apart so they don't stick together
        overlap = (2 * r) - dist
        x[idx_i] += (overlap / 2) * nx
        y[idx_i] += (overlap / 2) * ny
        x[idx_j] -= (overlap / 2) * nx
        y[idx_j] -= (overlap / 2) * ny

        # Calculate relative velocities
        dvx = vx[idx_i] - vx[idx_j]
        dvy = vy[idx_i] - vy[idx_j]
        rel_vel = dvx * nx + dvy * ny

        # Only apply momentum change if particles are moving towards each other
        approaching = rel_vel < 0

        # Equal mass elastic collision: swap velocities along the normal vector
        vx[idx_i][approaching] -= rel_vel[approaching] * nx[approaching]
        vy[idx_i][approaching] -= rel_vel[approaching] * ny[approaching]
        vx[idx_j][approaching] += rel_vel[approaching] * nx[approaching]
        vy[idx_j][approaching] += rel_vel[approaching] * ny[approaching]

    if (step + 1) % save_every == 0:
        frames_sx.append(x.copy())
        frames_sy.append(y.copy())
        frames_bX.append(X_big)
        frames_bY.append(Y_big)
        frames_t.append(step * dt)

print(f"Simulated {n_steps} steps  ({n_steps*dt:.1f} ps)  ->  {len(frames_t)} frames")
print(f"Final position:  ({X_big:.3f}, {Y_big:.3f}) nm")

# ── UI & Animation ────────────────────────────────────────────────
fig = plt.figure(figsize=(10, 8))
fig.subplots_adjust(bottom=0.2) # Make room for the slider and button

ax = fig.add_subplot(111)
ax.set_aspect("equal")
ax.axis("off")

border = plt.Rectangle((0, 0), a, a, fill=False, edgecolor=CMAP['MUTED'], linewidth=2)
ax.add_patch(border)

large_circle = plt.Circle((frames_bX[0], frames_bY[0]), R,
                          edgecolor=CMAP['PINK'], facecolor='none',
                          linewidth=2)
ax.add_patch(large_circle)

small_pts, = ax.plot(frames_sx[0], frames_sy[0], 'o',
                     color=CMAP['DATA'], markersize=3, alpha=0.5)

trail_line, = ax.plot(frames_bX[:1], frames_bY[:1], '-',
                      color=CMAP['ACCENT'], linewidth=1.5, alpha=0.8)

title = ax.set_title(f"Brownian Motion  |  t = 0 ps", fontsize=14, fontweight='bold')

# --- Zoom Slider Setup ---
ax_zoom = plt.axes([0.15, 0.08, 0.5, 0.03]) # [left, bottom, width, height]
zoom_slider = Slider(
    ax=ax_zoom,
    label='Zoom Level',
    valmin=0.5,     # < 1.0 zooms out
    valmax=5.0,     # > 1.0 zooms in
    valinit=1.0,
    color=CMAP.get('ACCENT', 'blue')
)

# --- Tracking Toggle Button Setup ---
ax_track = plt.axes([0.72, 0.08, 0.18, 0.03]) # Matched height and position with slider
track_btn = Button(
    ax=ax_track,
    label='Tracking: OFF',
    color=CMAP.get('MUTED', '0.8'),
    hovercolor=CMAP.get('ACCENT', '0.6')
)
track_btn.label.set_fontweight('bold')

class UIState:
    is_tracking = False

def toggle_track(event):
    UIState.is_tracking = not UIState.is_tracking
    if UIState.is_tracking:
        track_btn.label.set_text('Tracking: ON')
        track_btn.color = CMAP.get('ACCENT', '0.6')
    else:
        track_btn.label.set_text('Tracking: OFF')
        track_btn.color = CMAP.get('MUTED', '0.8')
    fig.canvas.draw_idle()

track_btn.on_clicked(toggle_track)

def animate(i):
    large_circle.center = (frames_bX[i], frames_bY[i])
    small_pts.set_data(frames_sx[i], frames_sy[i])
    trail_line.set_data(frames_bX[:i + 1], frames_bY[:i + 1])
    title.set_text(f"Brownian Motion  |  t = {frames_t[i]:.1f} ps")

    # --- DYNAMIC ZOOM & TRACKING LOGIC ---
    zoom = zoom_slider.val

    if UIState.is_tracking:
        center_x, center_y = frames_bX[i], frames_bY[i]
    else:
        # Keep camera centered on the box
        center_x, center_y = a / 2, a / 2

    # Calculate new boundaries based on slider value
    view_span = a / zoom
    ax.set_xlim(center_x - (view_span / 2), center_x + (view_span / 2))
    ax.set_ylim(center_y - (view_span / 2), center_y + (view_span / 2))

    return large_circle, small_pts, trail_line, title

ani = animation.FuncAnimation(fig, animate, frames=len(frames_t), blit=False, interval=20)
plt.show()
