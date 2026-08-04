"""
Brownian motion simulation - Python port of Dr F's MATLAB code
-----------------------------------------------------------------
Models 2D collisions (and subsequent motion) of a large circular particle
of mass M and radius R with N particles of mass m and radius r, in random
motion. This is a model of the Brownian motion of an observable particle
(e.g. under a microscope, such as pollen grains or soot), 'jostled' by
smaller air molecules (that can't be seen because they are smaller than
the wavelength of visible light).

To keep things simple, collisions between the small particles themselves
are NOT computed directly. Instead, a random walk (constant speed v, but
random direction after each collision) is used to model the effect that
those small-molecule collisions would have: after every dt = Kn*r/v
(Kn = Knudsen number), each small particle's direction is re-randomized.
Only large-small ("M-m") collisions are computed explicitly, via
conservation of momentum plus a coefficient of restitution C.

Units: positions in nm, time in picoseconds (ps), so speed is nm/ps.
Gravity is ignored -- on a picosecond timescale its effect is negligible
(9.8 m/s^2 = 9.8e-15 nm/ps^2).

Python port notes / adaptation from the original MATLAB:
    - The large particle starts FROM REST (Vx = Vy = 0), matching the
      original assignment ("determine the motion... if it starts from
      rest"). In Dr F's MATLAB code the large particle instead starts
      with its own thermal speed V at a random angle -- change
      V_INITIAL_FROM_REST to False below to reproduce that instead.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

rng = np.random.default_rng(1)

# ----------------------- Physical parameters -----------------------
N = 1000                     # number of small particles, mass m, radius r
T = 100.0                    # temperature of particles, deg C
m = 28.96e-3 / 6.02e23       # mass of a small particle e.g. air molecule (kg)
M = 10 * m                   # mass of the large particle e.g. soot (kg)
r = 0.16                     # radius of a small particle (nm)
R = 10 * r                   # radius of the large particle (nm)
a = 7 * R                    # size of the modelling scene (nm) - not a walled box
C = 1.0                      # coefficient of restitution (1 = perfectly elastic)
kB = 1.38e-23                # Boltzmann constant (J/K)

V_INITIAL_FROM_REST = True   # large particle starts at rest, per the assignment

# ----------------------- Derived quantities -----------------------
# average speeds from kinetic theory: (1/2)m<v^2> = (3/2)kT
v = np.sqrt(3 * kB * (T + 273) / m)   # small particle speed (m/s)
V = np.sqrt(3 * kB * (T + 273) / M)   # large particle thermal speed (m/s)
v /= 1000.0    # convert m/s -> nm/ps  (1 m/s = 1e-3 nm/ps)
V /= 1000.0

Kn = 15.0                     # Knudsen number: mean free path in units of r
dt = 0.01 * Kn * r / v        # timestep (ps), a fraction of mean free time
tmax = 200.0                  # max simulation time (ps)

# ----------------------- Helper functions -----------------------
def ball_displacement(x1, y1, x2, y2):
    """Distance and unit vector between two particle centres."""
    d = np.hypot(x2 - x1, y2 - y1)
    dhat = np.array([x2 - x1, y2 - y1]) / d
    return dhat, d


def bounce(x1, y1, x2, y2, ux1, uy1, ux2, uy2, C, M1, M2, R1, R2):
    """
    Resolve a possible 2D collision between particle 1 (mass M1, radius R1,
    position (x1,y1), incoming velocity (ux1,uy1)) and particle 2 (mass M2,
    radius R2, position (x2,y2), incoming velocity (ux2,uy2)).
    Returns updated (vx1,vy1,vx2,vy2,x1,y1,x2,y2).
    """
    u1 = np.array([ux1, uy1])
    u2 = np.array([ux2, uy2])
    vx1, vy1, vx2, vy2 = ux1, uy1, ux2, uy2

    dhat, d = ball_displacement(x1, y1, x2, y2)

    if d <= (R1 + R2):
        # push particles apart so they are exactly touching
        delta = (R1 + R2 - d) / 2
        x1, y1 = np.array([x1, y1]) - delta * dhat
        x2, y2 = np.array([x2, y2]) + delta * dhat

        # only resolve the collision if the particles are approaching
        if np.dot(u2 - u1, dhat) < 0:
            Vcm = (M1 * u1 + M2 * u2) / (M1 + M2)
            v1 = Vcm - C * (u1 - Vcm)
            v2 = Vcm - C * (u2 - Vcm)
            vx1, vy1 = v1
            vx2, vy2 = v2

    return vx1, vy1, vx2, vy2, x1, y1, x2, y2


# ----------------------- Initial positions -----------------------
X, Y = 0.5 * a, 0.5 * a  # large particle starts at the centre of the scene

if V_INITIAL_FROM_REST:
    Vx, Vy = 0.0, 0.0
else:
    theta0 = 2 * np.pi * rng.random()
    Vx, Vy = V * np.cos(theta0), V * np.sin(theta0)

# place small particles, checking they start further than r+R from the centre
x = np.zeros(N)
y = np.zeros(N)
for n in range(N):
    d = 0.0
    while d < (r + R):
        x[n] = r + rng.random() * (a - 2 * r)
        y[n] = r + rng.random() * (a - 2 * r)
        _, d = ball_displacement(x[n], y[n], X, Y)

# initial velocities of small particles: speed v, random direction
theta = 2 * np.pi * rng.random(N)
vx = v * np.cos(theta)
vy = v * np.sin(theta)

# ----------------------- Time-stepping simulation -----------------------
n_steps = int(np.ceil(tmax / dt))
save_every = max(1, n_steps // 300)   # keep ~300 animation frames

t = 0.0
tt = 0.0   # time since small particles last had their directions randomized

traj_X, traj_Y = [X], [Y]
frames_small_x, frames_small_y = [x.copy()], [y.copy()]
frames_large_X, frames_large_Y = [X], [Y]
frames_t = [0.0]

for step in range(n_steps):
    t += dt
    tt += dt

    # advance positions at constant velocity
    X += Vx * dt
    Y += Vy * dt
    x += vx * dt
    y += vy * dt

    # check every small particle against the large one for a collision
    for n in range(N):
        Vx, Vy, vx[n], vy[n], X, Y, x[n], y[n] = bounce(
            X, Y, x[n], y[n], Vx, Vy, vx[n], vy[n], C, M, m, R, r
        )

    traj_X.append(X)
    traj_Y.append(Y)

    # randomize small-particle directions once the mean free time has elapsed
    # (this stands in for the intermolecular collisions we're not simulating)
    if tt > Kn * r / v:
        tt = 0.0
        theta = 2 * np.pi * rng.random(N)
        vx = v * np.cos(theta)
        vy = v * np.sin(theta)

    if (step + 1) % save_every == 0:
        frames_small_x.append(x.copy())
        frames_small_y.append(y.copy())
        frames_large_X.append(X)
        frames_large_Y.append(Y)
        frames_t.append(t)

print(f"Simulated {n_steps} steps ({t:.1f} ps), {len(frames_t)} animation frames")
print(f"Small-particle speed v = {v:.4f} nm/ps, large-particle thermal speed V = {V:.4f} nm/ps")
print(f"Final large-particle position: ({X:.3f}, {Y:.3f}) nm")

# ----------------------- Animation -----------------------
fig, ax = plt.subplots(figsize=(7, 7))
ax.set_xlim(0, a)
ax.set_ylim(0, a)
ax.set_aspect("equal")
ax.axis("off")

theta_circle = np.linspace(0, 2 * np.pi, 100)
large_patch = plt.Circle((frames_large_X[0], frames_large_Y[0]), R, color="r", fill=False, linewidth=2)
ax.add_patch(large_patch)

small_pts, = ax.plot(frames_small_x[0], frames_small_y[0], "b*", ms=4)
snail_line, = ax.plot(frames_large_X[:1], frames_large_Y[:1], "r-", linewidth=1)
title = ax.set_title(f"Brownian motion simulation: t = 0 ps", fontsize=14)

ax.plot([0, a, a, 0, 0], [0, 0, a, a, 0], "k-", linewidth=3)


def update(i):
    large_patch.center = (frames_large_X[i], frames_large_Y[i])
    small_pts.set_data(frames_small_x[i], frames_small_y[i])
    snail_line.set_data(frames_large_X[:i + 1], frames_large_Y[:i + 1])
    title.set_text(f"Brownian motion simulation: t = {frames_t[i]:.1f} ps")
    return large_patch, small_pts, snail_line, title


ani = animation.FuncAnimation(fig, update, frames=len(frames_t), blit=False, interval=40)
ani.save("brownian_motion_drf.gif", writer="pillow", fps=25)
plt.close(fig)

# ----------------------- Static trajectory plot -----------------------
fig2, ax2 = plt.subplots(figsize=(6, 6))
ax2.plot(traj_X, traj_Y, "r-", lw=1)
ax2.plot(traj_X[0], traj_Y[0], "go", label="start")
ax2.plot(traj_X[-1], traj_Y[-1], "ks", label="end")
ax2.set_aspect("equal")
ax2.set_xlabel("x (nm)")
ax2.set_ylabel("y (nm)")
ax2.set_title("Large particle trajectory (Brownian motion)")
ax2.legend()
fig2.savefig("large_particle_trajectory_drf.png", dpi=150, bbox_inches="tight")