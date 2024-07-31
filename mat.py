import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from IPython.display import HTML  # For displaying animations in Jupyter notebooks

# Example data
A = np.array([(1, 1, 1), (3, 3, 3), (5, 1, 1)])  # Points to be connected
B = np.array([(i, i, i) for i in range(6)])      # All points for travel

# Unzip the coordinates for easier plotting
x_A, y_A, z_A = A[:,0], A[:,1], A[:,2]
x_B, y_B, z_B = B[:,0], B[:,1], B[:,2]

# Create a figure and a 3D axis
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Initial plot
line_A, = ax.plot([], [], [], 'ro-', markersize=8, label='Points A')  # Line for A
scatter_B = ax.scatter(x_B, y_B, z_B, color='blue', label='Points B')  # Scatter for B

def init():
    ax.set_xlim(min(x_B)-1, max(x_B)+1)
    ax.set_ylim(min(y_B)-1, max(y_B)+1)
    ax.set_zlim(min(z_B)-1, max(z_B)+1)
    return line_A, scatter_B

def update(frame):
    # Update the data for the points and lines
    if frame < len(x_A):
        line_A.set_data(x_A[:frame+1], y_A[:frame+1])
        line_A.set_3d_properties(z_A[:frame+1])
    return line_A, scatter_B

# Create the animation
ani = FuncAnimation(fig, update, frames=len(x_A), init_func=init, blit=True, repeat=False)

# Display animation in Jupyter Notebook
if 'IPython' in globals():
    HTML(ani.to_jshtml())
else:
    plt.show()
