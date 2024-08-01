import matplotlib.pyplot as plt

# Define the function
def func(x):
    return 2 * x + 4

# Generate 10 coordinates
x_values = list(range(10))
y_values = [func(x) for x in x_values]

# Split the coordinates into two segments
x_values_part1 = x_values[:5]  # First 5 points
y_values_part1 = y_values[:5]

x_values_part2 = x_values[5:]  # Last 5 points
y_values_part2 = y_values[5:]

# Plot the first part
plt.plot(x_values_part1, y_values_part1, marker='o', linestyle='-', color='b', label='Part 1')

# Plot the second part
plt.plot(x_values_part2, y_values_part2, marker='o', linestyle='-', color='r', label='Part 2')

# Add labels and title
plt.xlabel('x')
plt.ylabel('y')
plt.title('Plot of y = 2x + 4 with Two Separate Lines')

# Add legend
plt.legend()

# Show grid
plt.grid(True)

# Show the plot
plt.show()
