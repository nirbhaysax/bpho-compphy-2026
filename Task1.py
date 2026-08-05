import numpy as np
import matplotlib.pyplot as plt

def random_walk(N, s):
    """
    Generate a 2D random walk.
    N: number of steps
    s: step size
    """
    x = np.zeros(N)
    y = np.zeros(N)
    
    for n in range(1, N):
        theta = 2 * np.pi * np.random.rand()
        x[n] = x[n-1] + s * np.cos(theta)
        y[n] = y[n-1] + s * np.sin(theta)
    
    return x, y

# Example usage
N = 5000   # number of steps
s = 1      # step size

x, y = random_walk(N, s)

plt.figure(figsize=(6, 6))
plt.plot(x, y, linewidth=1)
plt.title(f"Random walk. Step size = {s}")
plt.xlabel("x")
plt.ylabel("y")
plt.axis("equal")
plt.grid(True, linestyle=":")
plt.show()
