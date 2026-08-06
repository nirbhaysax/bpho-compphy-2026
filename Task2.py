"""
Task 2: Brownian Motion Simulation
===================================
Models the 2D Brownian motion of a large observable particle (mass M, radius R)
colliding with N smaller particles (mass m, radius r) in random thermal motion.

Small-particle collisions are approximated via periodic direction randomization
(Knudsen-number based).  Large-small collisions use conservation of momentum
with a coefficient of restitution C.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from bpho_theme import apply_theme

CMAP = apply_theme()

rng = np.random.default_rng(1)

# ── Physical parameters ───────────────────────────────────────────
N      = 250                      # small particles (reduced for speed)
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
dt = 0.02 * Kn * r / v             # timestep (ps) — slightly larger = faster
tmax = 200.0                       # total simulation time (ps)


# ── Collision resolver (scalar args — no tuple allocations) ─────────
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

    # push apart
    delta = (sumR - d) / 2
    X -= delta * dx
    Y -= delta * dy
    x_i += delta * dx
    y_i += delta * dy

    # relative velocity along the contact normal
    rel_vel = (x_i - X) * dx + (y_i - Y) * dy
    if rel_vel >= 0:   # not approaching → no momentum transfer
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
# Rejection-sample any that landed too close to the centre
for n in range(N):
    while (x[n] - X_big)**2 + (y[n] - Y_big)**2 < (r + R)**2:
        x[n] = rng.uniform(2 * (r + R), a - 2 * (r + R))
        y[n] = rng.uniform(2 * (r + R), a - 2 * (r + R))

theta0 = 2 * np.pi * rng.random(N)
vx = v * np.cos(theta0)
vy = v * np.sin(theta0)

# ── Time stepping ─────────────────────────────────────────────────
n_steps = int(np.ceil(tmax / dt))
save_every = max(1, n_steps // 180)   # more frames, smoother animation

frames_sx, frames_sy = [x.copy()], [y.copy()]
frames_bX, frames_bY = [X_big], [Y_big]
frames_t = [0.0]

tt = 0.0
for step in range(n_steps):
    tt += dt

    # Euler step
    X_big += Vx * dt
    Y_big += Vy * dt
    x += vx * dt
    y += vy * dt

    # Vectorised collision check — compute all distances at once
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

    # Periodic direction randomization of small particles
    if tt > 0.08:   # fixed interval — much cleaner
        tt = 0.0
        theta = 2 * np.pi * rng.random(N)
        vx = v * np.cos(theta)
        vy = v * np.sin(theta)

    if (step + 1) % save_every == 0:
        frames_sx.append(x.copy())
        frames_sy.append(y.copy())
        frames_bX.append(X_big)
        frames_bY.append(Y_big)
        frames_t.append(step * dt)

print(f"Simulated {n_steps} steps  ({n_steps*dt:.1f} ps)  ->  {len(frames_t)} frames")
print(f"Final position:  ({X_big:.3f}, {Y_big:.3f}) nm")

# ── Animation ─────────────────────────────────────────────────────
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)
ax.set_xlim(0, a)
ax.set_ylim(0, a)
ax.set_aspect("equal")
ax.axis("off")

border = plt.Rectangle((0, 0), a, a, fill=False, edgecolor=CMAP['MUTED'],
                        linewidth=2)
ax.add_patch(border)

large_circle = plt.Circle((frames_bX[0], frames_bY[0]), R,
                          edgecolor=CMAP['PINK'], facecolor='none',
                          linewidth=2)
ax.add_patch(large_circle)

small_pts, = ax.plot(frames_sx[0], frames_sy[0], 'o',
                     color=CMAP['DATA'], markersize=3, alpha=0.5)

trail_line, = ax.plot(frames_bX[:1], frames_bY[:1], '-',
                      color=CMAP['ACCENT'], linewidth=1.5, alpha=0.8)

title = ax.set_title(f"Brownian Motion  |  t = 0 ps", fontsize=14,
                     fontweight='bold')


def animate(i):
    large_circle.center = (frames_bX[i], frames_bY[i])
    small_pts.set_data(frames_sx[i], frames_sy[i])
    trail_line.set_data(frames_bX[:i + 1], frames_bY[:i + 1])
    title.set_text(f"Brownian Motion  |  t = {frames_t[i]:.1f} ps")
    return large_circle, small_pts, trail_line, title


ani = animation.FuncAnimation(fig, animate, frames=len(frames_t),
                              blit=False, interval=20)

plt.show()